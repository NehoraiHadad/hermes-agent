"""Tests for gateway.whatsapp_identity alias resolution path."""

import json

from gateway.whatsapp_identity import (
    canonical_whatsapp_identifier,
    expand_whatsapp_aliases,
)
from hermes_constants import reset_hermes_home_override, set_hermes_home_override


def test_aliases_resolve_on_modern_platforms_layout(tmp_path, monkeypatch):
    tmp_home = tmp_path / "hermes-home"
    mapping_dir = tmp_home / "platforms" / "whatsapp" / "session"
    mapping_dir.mkdir(parents=True, exist_ok=True)
    (mapping_dir / "lid-mapping-999999999999999.json").write_text(
        json.dumps("15551234567@s.whatsapp.net"),
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_HOME", str(tmp_home))

    assert expand_whatsapp_aliases("999999999999999@lid") == {
        "999999999999999",
        "15551234567",
    }


def test_aliases_resolve_from_process_home_inside_profile_scope(tmp_path, monkeypatch):
    process_home = tmp_path / "hermes-home"
    mapping_dir = process_home / "platforms" / "whatsapp" / "session"
    mapping_dir.mkdir(parents=True, exist_ok=True)
    (mapping_dir / "lid-mapping-999999999999999.json").write_text(
        json.dumps("15551234567@s.whatsapp.net"), encoding="utf-8"
    )
    monkeypatch.setenv("HERMES_HOME", str(process_home))
    profile_home = process_home / "profiles" / "village"
    profile_home.mkdir(parents=True)

    token = set_hermes_home_override(str(profile_home))
    try:
        assert expand_whatsapp_aliases("999999999999999@lid") == {
            "999999999999999",
            "15551234567",
        }
        assert canonical_whatsapp_identifier("999999999999999@lid") == "15551234567"
    finally:
        reset_hermes_home_override(token)


