import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import types
import services.stripe_service as ss


def test_list_invoices_without_stripe(monkeypatch):
    monkeypatch.setattr(ss, "stripe", None)
    assert ss.list_invoices() == []


def test_list_invoices_without_key(monkeypatch):
    fake = types.SimpleNamespace(api_key="")
    monkeypatch.setattr(ss, "stripe", fake)
    assert ss.list_invoices() == []


def test_list_invoices_success(monkeypatch):
    class FakeInvoiceObj:
        def __init__(self, id):
            self.id = id
        def to_dict_recursive(self):
            return {"id": self.id}
    class FakeResp:
        data = [FakeInvoiceObj("inv_1"), FakeInvoiceObj("inv_2")]
    class FakeStripe(types.SimpleNamespace):
        def __init__(self):
            super().__init__(api_key="key", Invoice=types.SimpleNamespace(list=lambda limit: FakeResp()))
    monkeypatch.setattr(ss, "stripe", FakeStripe())
    invoices = ss.list_invoices()
    assert invoices == [{"id": "inv_1"}, {"id": "inv_2"}]
