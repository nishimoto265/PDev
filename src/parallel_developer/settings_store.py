"""Persistence helper for CLI settings stored in .parallel-dev/settings.yaml."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass
class SettingsData:
    attach_mode: str = "auto"
    boss_mode: str = "score"
    flow_mode: str = "manual"
    auto_commit: bool = False
    worker_count: int = 3
    session_mode: str = "parallel"


class SettingsStore:
    """Load and persist CLI configuration flags."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._legacy_json = self._path.with_suffix(".json") if self._path.suffix in {".yaml", ".yml"} else None
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

    @property
    def worker_count(self) -> int:
        return self._data.worker_count

    @worker_count.setter
    def worker_count(self, value: int) -> None:
        self._data.worker_count = value
        self._save()

    @property
    def session_mode(self) -> str:
        return self._data.session_mode

    @session_mode.setter
    def session_mode(self, value: str) -> None:
        self._data.session_mode = value
        self._save()

    def snapshot(self) -> Dict[str, object]:
        return {
            "attach_mode": self._data.attach_mode,
            "boss_mode": self._data.boss_mode,
            "flow_mode": self._data.flow_mode,
            "auto_commit": self._data.auto_commit,
            "worker_count": self._data.worker_count,
            "session_mode": self._data.session_mode,
        }

    def update(
        self,
        *,
        attach_mode: Optional[str] = None,
        boss_mode: Optional[str] = None,
        flow_mode: Optional[str] = None,
        auto_commit: Optional[bool] = None,
        worker_count: Optional[int] = None,
        session_mode: Optional[str] = None,
    ) -> None:
        if attach_mode is not None:
            self._data.attach_mode = attach_mode
        if boss_mode is not None:
            self._data.boss_mode = boss_mode
        if flow_mode is not None:
            self._data.flow_mode = flow_mode
        if auto_commit is not None:
            self._data.auto_commit = auto_commit
        if worker_count is not None:
            self._data.worker_count = worker_count
        if session_mode is not None:
            self._data.session_mode = session_mode
        self._save()

    def _load(self) -> SettingsData:
        payload: Dict[str, object]
        if self._path.exists():
            try:
                payload = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                payload = {}
        elif self._legacy_json and self._legacy_json.exists():
            try:
                payload = json.loads(self._legacy_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                payload = {}
        else:
            payload = {}
        return SettingsData(
            attach_mode=str(payload.get("attach_mode", "auto")),
            boss_mode=str(payload.get("boss_mode", "score")),
            flow_mode=str(payload.get("flow_mode", "manual")),
            auto_commit=bool(payload.get("auto_commit", False)),
            worker_count=int(payload.get("worker_count", 3)),
            session_mode=str(payload.get("session_mode", "parallel")),
        )

    def _save(self) -> None:
        try:
            self._path.write_text(
                yaml.safe_dump(self.snapshot(), sort_keys=True, allow_unicode=True),
                encoding="utf-8",
            )
        except OSError:
            pass
