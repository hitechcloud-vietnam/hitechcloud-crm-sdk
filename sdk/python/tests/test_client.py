"""Basic structural tests for the HiTechCloud CRM Python SDK."""

from hitechcloud_crm import CRMClient, verify_signature, compute_signature
from hitechcloud_crm.resources import CrudResource, RESOURCE_PATHS


def make_client():
    return CRMClient(token="crm_at_test", base_url="https://crm-gateways-sandbox.hitechcloud.vn")


def test_client_exposes_all_resources():
    crm = make_client()
    for accessor in RESOURCE_PATHS:
        assert isinstance(getattr(crm, accessor), CrudResource)
    assert crm.files is not None
    assert crm.webhooks is not None
    assert crm.imports is not None
    assert crm.exports is not None


def test_crud_paths():
    crm = make_client()
    assert crm.contacts._path == "contacts"
    assert crm.custom_fields._path == "custom-fields"
    assert crm.lead_sources._path == "lead-sources"


def test_bulk_guard():
    crm = make_client()
    try:
        crm.companies.bulk([{"op": "create", "data": {}}])
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for non-bulk resource")


def test_webhook_signature_roundtrip():
    secret = "whsec_6b3c15aa"
    body = '{"event":"deal.won","id":"evt_1"}'
    sig = compute_signature(body, secret)
    assert verify_signature(body, sig, secret) is True
    assert verify_signature(body, "deadbeef", secret) is False
    assert verify_signature(body, "", secret) is False
