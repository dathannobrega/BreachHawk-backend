import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.leak_mongo import LeakDoc


def test_leakdoc_example_present():
    config = getattr(LeakDoc, "model_config", LeakDoc.Config)
    if isinstance(config, dict):
        example = config.get("json_schema_extra") or config.get("schema_extra")
    else:
        example = getattr(config, "json_schema_extra", None) or getattr(config, "schema_extra", None)
    assert example and "example" in example
    assert example["example"]["site_id"] == 1
