import os
import json
import pytest
from core.config import replace_env_placeholders, load_json_config

def test_replace_env_placeholders():
    os.environ["TEST_VAR"] = "test_value"
    config = {"key": "${TEST_VAR}", "list": ["${TEST_VAR}", "plain"]}
    replaced = replace_env_placeholders(config)
    assert replaced["key"] == "test_value"
    assert replaced["list"][0] == "test_value"
    assert replaced["list"][1] == "plain"

def test_replace_env_placeholders_missing():
    if "MISSING_VAR" in os.environ:
        del os.environ["MISSING_VAR"]
    config = {"key": "${MISSING_VAR}"}
    replaced = replace_env_placeholders(config)
    assert replaced["key"] == "${MISSING_VAR}"

def test_load_json_config_existing(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "test.json"
    config_file.write_text(json.dumps({"foo": "bar"}))
    
    # Patch the global CONFIG_DIR in core.config
    import core.config
    monkeypatch.setattr(core.config, "CONFIG_DIR", str(config_dir))
    
    config = load_json_config("test.json")
    assert config == {"foo": "bar"}

def test_load_json_config_non_existent():
    config = load_json_config("non_existent.json")
    assert config == {}
