"""Visit envelopeni Smartup sync endpointga yuborish flowi."""

import json

from tests.smoke.clients.visit_sync import (
    MinimalVisit,
    OrderVisit,
    parse_visit_sync_response,
)
from tests.smoke.flows.flow_mobile_authorization import request_mobile_business


VISIT_SYNC_PATH = "/b/biruni/mt/sync:sync"


def sync_visit(authorization, visit):
    """Bitta Visit envelopeni sync qilib ``VisitSyncResult`` qaytaradi."""
    if not isinstance(visit, (MinimalVisit, OrderVisit)):
        raise TypeError(
            "sync_visit(): visit MinimalVisit yoki OrderVisit bo'lishi kerak"
        )

    response = request_mobile_business(
        authorization,
        "POST",
        VISIT_SYNC_PATH,
        headers={"Content-Type": "text/plain"},
        data=json.dumps(
            visit.envelope,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    authorization.api.require_success(response, operation="mobile visit sync")
    return parse_visit_sync_response(response.text, entry_id=visit.entry_id)
