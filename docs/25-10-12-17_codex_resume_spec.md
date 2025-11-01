## Codex CLI `resume` 調査メモ（2025-10-12 17:00）

### 現行仕様の要点
- `codex resume` は `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` を探索し、選択したロールアウトファイルからセッションを再構築する。
- CLI フラグは通常起動と同様に有効。例: `codex resume --last -m gpt-5`、`codex resume <SESSION_ID> --search` 等。
- ピッカー表示（引数なし）、最新セッションの直接再開（`--last`）、UUID 指定での復帰の 3 パターンがサポートされる。
- TUI 側は `ResumeSelection::Resume(path)` を受けると `ConversationManager::resume_conversation_from_rollout` を呼び出し、過去の会話コンテキストを含む `CodexConversation` を復元して `ChatWidget::new_from_existing` に渡す。
- 復元時はセッション ID を維持したまま新しい `RolloutRecorder` を再アタッチし、履歴の追記やトークン使用量追跡を継続できる。

### JSONL から復元される情報
- `RolloutRecorder::get_rollout_history` がロールアウトを `Vec<RolloutItem>` にパースし、`SessionMeta` や `TurnContext`、`EventMsg` など非メッセージ項目も保持したまま `InitialHistory::Resumed` を生成する。
- `RolloutItem` にはコマンド実行ログ、Plan 更新、MCP 関連イベント、モデル構成変更などが含まれ、単なるメッセージ履歴以上の状態を復元可能。
- `ChatWidget::new_from_existing` と `spawn_agent_from_existing` が `SessionConfigured` を即座に投げ直し、TUI 上で差分ビューや承認ダイアログなどの履歴を再表示する。

### 旧仕様との違い
- 0.36.0（2025-09-15）以前は `codex resume` / `codex --resume` が未実装で、ロールアウトを直接閲覧する以外に継続不可だった。
- 0.46.0（2025-10-09 現在）では終了時に再開コマンドをリマインドするなど、レジューム前提の UX 改善が入っている。

### 確認に使った主なコマンド
- `codex --version`
- `codex resume --help`
- `git clone --depth=1 https://github.com/openai/codex.git`
- `rg "codex resume" -n`
- `sed -n '400,470p' codex-rs/tui/src/lib.rs`
- `sed -n '200,340p' codex-rs/core/src/rollout/recorder.rs`
