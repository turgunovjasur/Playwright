"""Readiness belongs to one prepared resource, never to its unrelated siblings."""


def resource_ready(data, name):
    """Only a completed resource verification is a usable precondition."""
    return data.get("ready", {}).get(name) == "passed"


def resource_status(data, name, status):
    if status not in {"process", "passed", "failed"}:
        raise ValueError("Noma’lum tayyorlov resursi holati")
    data.setdefault("ready", {})[name] = status
