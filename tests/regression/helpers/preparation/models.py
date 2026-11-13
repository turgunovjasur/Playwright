"""Small preparation contracts shared by explicit runner steps."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PreparationSpec:
    key: str
    scope: str
    parameters: dict
    requires: tuple[str, ...] = ()


@dataclass
class PreparationResult:
    status: str  # ready / missing / partial; unknown must raise, never return missing
    entities: dict = field(default_factory=dict)
    detail: str = ""
    evidence: dict = field(default_factory=dict)
