"""Setup verification failures that leave a verified, usable baseline."""


class SetupDependencyReadyError(AssertionError):
    """Fail the check after all data required by dependent tests is verified."""
