"""Run-local durable registry. Retry writes a child copy, never its source."""
from copy import deepcopy
from datetime import datetime, timezone
from tests.regression.runtime import run_directory
from tests.regression.retry.state import ACTIVE, RetryBlocked, digest, read, write


class Registry:
    def __init__(self, baseline):
        journal = ACTIVE.get()
        if journal is None:
            raise RuntimeError("Tayyorlov faqat regression runner ichida bajariladi")
        self.journal = journal
        config = journal.item.config
        self.path = run_directory(config) / "preparations.json"
        context = {k: baseline[k] for k in ("url", "company_code", "filial_id")}
        context["baseline_signature"] = baseline.get("_baseline_signature", digest(baseline))
        if self.path.exists():
            self.data = read(self.path)
        else:
            source = getattr(config, "_retry_plan", {}).get("preparations")
            self.data = deepcopy(source) if source else {
                "version": 1, "context": context, "root_run": run_directory(config).name,
                "entries": {}, "events": []}
        if self.data.get("version") != 1 or self.data["context"] != context:
            raise RetryBlocked("Tayyorlov registri baseline yoki muhitga mos emas")

    def identity(self, spec):
        return digest({"context": self.data["context"], "scope": spec.scope,
                       "key": spec.key, "parameters": spec.parameters})

    def entry(self, spec):
        key = self.identity(spec)
        return self.data["entries"].setdefault(key, {
            "key": spec.key, "scope": spec.scope, "parameters": spec.parameters,
            "attempts": 0, "entities": {}, "status": "pending", "owner_node": self.journal.item.nodeid})

    def recover_journal(self, spec):
        """A later setup wrapper may finish the same preparation safely."""
        from pathlib import Path
        from tests.regression.runtime import ROOT
        for relative in self.entry(spec).get("journals", []):
            path = (ROOT / "test-results/runs" / relative).resolve()
            if not path.is_relative_to(ROOT / "test-results/runs") or not path.is_file():
                raise RetryBlocked("Tayyorlov operatsiya dalili topilmadi")
            if path == self.journal.directory / "retry-journal.json":
                continue
            previous = read(path)
            for key, operation in previous.get("operations", {}).items():
                self.journal.source.setdefault("operations", {}).setdefault(key, operation)

    def remember_journal(self, spec):
        from tests.regression.runtime import ROOT
        relative = str((self.journal.directory / "retry-journal.json").relative_to(ROOT / "test-results/runs"))
        paths = self.entry(spec).setdefault("journals", [])
        if relative not in paths:
            paths.append(relative)
        self.save()

    def save(self):
        write(self.path, self.data)

    def event(self, spec, action, **fields):
        self.data["events"].append({"time": datetime.now(timezone.utc).isoformat(),
            "key": spec.key, "scope": spec.scope, "action": action,
            "nodeid": self.journal.item.nodeid, **fields})
        self.save()

    def checkpoint(self, spec, **entities):
        """Persist IDs immediately, including before the parent test passes."""
        self.entry(spec)["entities"].update(entities)
        self.event(spec, "confirmed_entities", entities=entities)

