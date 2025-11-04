"""Persistence helper for CLI settings stored in .parallel-dev/settings.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SettingsData:
    attach_mode: str = "auto"
    codex_home_mode: str = "session"
    boss_mode: str = "score"


class SettingsStore:
    """Load and persist CLI configuration flags."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: SettingsData = self._load()

    @property
    def attach_mode(self) -> str:
        return self._data.attach_mode

    @attach_mode.setter
    def attach_mode(self, value: str) -> None:
        self._data.attach_mode = value
        self._save()

    @property
    def codex_home_mode(self) -> str:
        return self._data.codex_home_mode

    @codex_home_mode.setter
    def codex_home_mode(self, value: str) -> None:
        self._data.codex_home_mode = value
        self._save()

    @property
    def boss_mode(self) -> str:
        return self._data.boss_mode

    @boss_mode.setter
    def boss_mode(self, value: str) -> None:
        self._data.boss_mode = value
        self._save()

    def snapshot(self) -> Dict[str, str]:
        return {
            "attach_mode": self._data.attach_mode,
            "codex_home_mode": self._data.codex_home_mode,
            "boss_mode": self._data.boss_mode,
        }

    def update(self, *, attach_mode: Optional[str] = None, codex_home_mode: Optional[str] = None, boss_mode: Optional[str] = None) -> None:
        if attach_mode is not None:
            self._data.attach_mode = attach_mode
        if codex_home_mode is not None:
            self._data.codex_home_mode = codex_home_mode
        if boss_mode is not None:
            self._data.boss_mode = boss_mode
        self._save()

    def _load(self) -> SettingsData:
        if not self._path.exists():
            return SettingsData()
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return SettingsData()
        return SettingsData(
            attach_mode=str(payload.get("attach_mode", "auto")),
            codex_home_mode=str(payload.get("codex_home_mode", "session")),
            boss_mode=str(payload.get("boss_mode", "score")),
        )

    def _save(self) -> None:
        data = self.snapshot()
        try:
            self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass
