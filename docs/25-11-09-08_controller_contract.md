# Controller Event / Store Contract (2025-11-09)

## ControllerEventType
- status: monitor status panel text.
- log: append message to log pane.
- log_copy/log_save: UI clipboard/save operations.
- scoreboard: scoreboard payload (dict).
- selection_request/selection_finished: prompt UI for candidate selection.
- pause_state: toggle paused view state.
- quit: request UI shutdown.

## Stores package
- `parallel_developer.stores.settings_store.SettingsStore`: YAML config persisted at `~/.parallel-dev/config.yaml`.
- `session_manifest.SessionManifest`: stores cycle artifacts + pane mapping.
- Modules consolidated under `parallel_developer/stores/` so all persistence entry points are in one namespace.
