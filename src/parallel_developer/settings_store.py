"""Persistence helper for CLI settings stored in .parallel-dev/settings.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SettingsData:
    attach_mode: str = "auto"
    boss_mode: str = "score"
    flow_mode: str = "manual"
    auto_commit: bool = False


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
    def boss_mode(self) -> str:
        return self._data.boss_mode

    @boss_mode.setter
    def boss_mode(self, value: str) -> None:
        self._data.boss_mode = value
        self._save()

    @property
    def flow_mode(self) -> str:
        return self._data.flow_mode

    @flow_mode.setter
    def flow_mode(self, value: str) -> None:
        self._data.flow_mode = value
        self._save()

    @property
    def auto_commit(self) -> bool:
        return self._data.auto_commit

    @auto_commit.setter
    def auto_commit(self, value: bool) -> None:
        self._data.auto_commit = value
        self._save()

    def snapshot(self) -> Dict[str, object]:
        return {
            "attach_mode": self._data.attach_mode,
            "boss_mode": self._data.boss_mode,
            "flow_mode": self._data.flow_mode,
            "auto_commit": self._data.auto_commit,
        }

    def update(self, *, attach_mode: Optional[str] = None, boss_mode: Optional[str] = None, flow_mode: Optional[str] = None, auto_commit: Optional[bool] = None) -> None:
        if attach_mode is not None:
            self._data.attach_mode = attach_mode
        if boss_mode is not None:
            self._data.boss_mode = boss_mode
        if flow_mode is not None:
            self._data.flow_mode = flow_mode
        if auto_commit is not None:
            self._data.auto_commit = auto_commit
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
            boss_mode=str(payload.get("boss_mode", "score")),
            flow_mode=str(payload.get("flow_mode", "manual")),
            auto_commit=bool(payload.get("auto_commit", False)),
        )

    def _save(self) -> None:
        data = self.snapshot()
        try:
            self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass
