"""Keep the current run and at most three complete, usable older runs."""
from datetime import datetime
from pathlib import Path
import json
import shutil


_OLD_RUN_LIMIT = 3
_FINISHED = {"passed", "failed", "blocked", "interrupted"}


def _object(path):
    if path.is_symlink():
        return {}
    try:
        data = json.loads(path.read_bytes())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _directories(parent):
    if not parent.is_dir() or parent.is_symlink():
        return []
    return [p for p in parent.iterdir() if p.is_dir() and not p.is_symlink()]


def _finished(meta):
    return bool(meta.get("completed_at_utc")) and meta.get("status") in _FINISHED


def _dependencies(meta):
    for key in ("retry_of", "resumed_from"):
        reference = meta.get(key)
        if isinstance(reference, dict) and isinstance(reference.get("run_id"), str):
            yield reference["run_id"]


def _started(meta):
    try:
        stamp = datetime.fromisoformat(meta["started_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is not None:
            return stamp.timestamp()
    except (KeyError, AttributeError, TypeError, ValueError, OverflowError):
        pass
    return float("-inf")


def prune_results(results, environment):
    """Prune owned run folders at startup; never touch legacy/shared output.

    Active runs and resume/retry sources occupy older-run slots. Dependencies
    stay with their run, even when that displaces a newer unrelated run. The
    newest older run is always retained. An impossible budget blocks startup
    before deleting anything. Without a current ID, reserve its future slot.
    """
    results = Path(results)
    runs_root = results / "runs"
    if not results.is_dir() or results.is_symlink() or runs_root.is_symlink():
        return
    directories = _directories(runs_root)
    runs = {}
    for run in directories:
        meta = _object(run / "run.json")
        if meta.get("run_id") == run.name:
            runs[run.name] = (run, meta)
    current = environment.get("REGRESSION_RUN_ID")
    old = set(runs) - {current}
    if not old:
        return

    def family(names):
        pending = list(names)
        found = set()
        while pending:
            name = pending.pop()
            if not name or name in found:
                continue
            if name not in runs:
                raise RuntimeError(
                    f"Run retention: {name!r} manba runi topilmadi yoki xavfsiz "
                    "run.json yo'q; hech qanday run o'chirilmadi."
                )
            found.add(name)
            pending.extend(_dependencies(runs[name][1]))
        return found - {current}

    newest = sorted(old, key=lambda name: (_started(runs[name][1]), name), reverse=True)
    required = {name for name, (_, meta) in runs.items() if not _finished(meta)}
    required.add(newest[0])
    if current in runs:
        required.add(current)
    resume = environment.get("ORDER_RESUME_RUN")
    if resume:
        required.add(resume)
    retry = environment.get("ORDER_RETRY_PLAN")
    if retry:
        required.add(Path(retry).parent.name)
    keep = family(required)
    if len(keep) > _OLD_RUN_LIMIT:
        raise RuntimeError(
            "Run retention: faol runlar, eng yangi run va resume/retry manbalari "
            f"uchun {len(keep)} eski run kerak, limit {_OLD_RUN_LIMIT}. "
            "Hech qanday run o'chirilmadi; avval faol runlar/manbalarni tekshiring."
        )
    for name in newest:
        if len(keep) == _OLD_RUN_LIMIT:
            break
        candidates = family({name})
        if len(keep | candidates) <= _OLD_RUN_LIMIT:
            keep.update(candidates)

    expired = [runs[name] for name in old - keep]
    # Validate the entire deletion plan before mutating any folder. A concurrent
    # run starting or changing state makes this pass fail safely.
    if set(_directories(runs_root)) != set(directories):
        raise RuntimeError("Run retention: run papkalari o'zgardi; o'chirish bekor qilindi.")
    for run, meta in runs.values():
        if run.is_symlink() or _object(run / "run.json") != meta:
            raise RuntimeError("Run retention: run holati o'zgardi; o'chirish bekor qilindi.")
    for run, _ in sorted(expired, key=lambda entry: (_started(entry[1]), entry[0].name)):
        shutil.rmtree(run)
