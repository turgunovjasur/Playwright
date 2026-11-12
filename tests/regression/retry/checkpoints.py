"""Explicit business checkpoints: reuse prior verified steps, never fabricate PASS."""
from decimal import Decimal
import allure
from tests.regression.retry.state import ACTIVE, _json_value


def value(name, data=None):
    journal = ACTIVE.get()
    if journal is None:
        return None
    if data is not None:
        journal.data.setdefault("values", {})[name] = _json_value(data)
        journal.save()
        return data
    previous = journal.source.get("values", {}).get(name)
    if previous is not None:
        journal.data.setdefault("values", {})[name] = previous
        journal.save()
    return previous


def verified(name):
    journal = ACTIVE.get()
    if journal:
        journal.data.setdefault("verified_steps", []).append(name)
        journal.save()


def reuse(name):
    journal = ACTIVE.get()
    if not journal or name not in journal.source.get("verified_steps", []):
        return False
    allure.attach("Bu bosqich dastlabki urinishda tekshirilgan. Hozir qayta mutatsiya bajarilmaydi; yakuniy server holati yana tekshiriladi.",
                  "Oldingi tasdiqlangan bosqich: " + name, allure.attachment_type.TEXT)
    verified(name)
    return True


def decimal_map(data):
    return {key: Decimal(str(number)) for key, number in data.items()}


def draft_or_reused_posted(row):
    """A retry may find its own initial-balance document already posted.

    Accept Y only if this exact document's post was previously attempted after
    the original draft assertions. Fresh runs must still observe N.
    """
    from tests.regression.retry.state import digest
    journal = ACTIVE.get()
    if row.get("posted") == "Y" and journal and journal.source:
        key = "api:anor/mkw/init_balance/init_inventory_balance_list:post:" + digest({"balance_id": str(row["balance_id"])})
        if key in journal.source.get("operations", {}):
            return "Y"
    return "N"
