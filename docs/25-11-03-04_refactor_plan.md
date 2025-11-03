# Parallel Developer リファクタ計画（UTC 2025-11-03 04:56）

## 現状整理
- `src/parallel_developer/cli.py` に Textual UI ウィジェット、CLIController、補助クラス、エントリーポイントが1ファイルで集約されており、約1500行規模になっている。
- `ParallelDeveloperApp` は UI 描画だけでなく、コマンドパレット制御・ショートカット処理・ログコピー・Manifest 更新など多数の責務を直接保持。
- `CLIController` は orchestrator 呼び出し、Manifest 永続化、tmux アタッチ制御、設定ロード、Textual イベント送出を一括で扱い、内部状態を UI が直接参照（例：`controller._config`）している。
- サービス層（`services.py`）や orchestrator との結合はプレーンな関数呼び出しで、依存注入ポイントが `build_orchestrator` のみ。UI 側がログ出力やステータス表示のたびに controller の内部詳細へアクセスする必要がある。
- UI イベントハンドラに重複実装や一貫性のない API（`on_option_list_option_selected` が2回定義される等）が混在し、バグ温床になりやすい。

## 課題
1. **責務分離の欠如**  
   - UI とアプリケーション制御が密結合で、単体テストや差分検証が困難。
2. **状態共有の脆さ**  
   - UI から controller の内部属性へ直接アクセスしており、構造変更時に容易に破綻する。
3. **拡張性の制約**  
   - 新しい入力モードやコマンドを追加する際に Textual 側イベントと controller 側ロジックの双方を修正する必要があり、変更範囲が読みにくい。
4. **バグ発生源**  
   - イベントハンドラ重複やキーバインド処理の複雑化が Shift+Enter 送信バグなどの再発に繋がっている。

## リファクタ目標
- UI（描画・入力・ショートカット処理）とアプリケーションロジック（指示管理・tmux制御・ログ保存）を明確に分割し、双方向依存を減らす。
- controller の公開 API を定義し、UI はその API 経由で状態を取得・更新する。
- コマンド体系（`/attach` など）を設定/ハンドラテーブル化し、テスト容易性を高める。
- Textual ウィジェットを再利用可能な粒度で整理し、UI テストとロジックテストの責務を分ける。

## 段階的リファクタ案

### フェーズ1: 依存境界の明確化
- `CLIController` を独立モジュールへ切り出し（例: `controller.py`）。公開メソッドとイベント種別を整理。
- `ParallelDeveloperApp` から controller の内部属性参照を排除し、必要な情報は専用データクラス（例: `ControllerState`）で受け取る。
- `EventLog`／`CommandPalette` など UI 専用クラスを `ui/widgets.py` に移動。
- 既存テストを調整し、フェーズ1完了時点で `uv run pytest` を緑に保つ。

### フェーズ2: コマンド処理のモジュール化
- コマンド仕様を `commands.py` などに集約し、CLIController は仕様に従ってディスパッチするだけにする。
- `/resume` 等で利用するオプション生成処理を pure function 化し、単体テストを追加。
- Textual 側はコマンド候補表示専用のインターフェイスを介して suggestions を取得する。

### フェーズ3: UI フローの簡素化
- `ParallelDeveloperApp` のキーハンドラ・クリックハンドラをプレーンメソッドへ分割し、重複定義を解消。
- Command palette / selection list 表示状態をステートマシン（`Enum` など）で管理し、分岐の複雑度を低減。
- UI テストは Textual の `run_test` ベースを維持しつつ、新しいハンドラテストを追加。

### フェーズ4: ログ/Manifest ハンドリングの抽象化
- ログ保存やステータス通知を controller のイベントとして扱い、UI は subscribe するだけにする。
- Manifest 更新処理も controller 側に閉じ込め、UI は「セッション選択→結果受信」という形で操作。

## テスト戦略
- 各フェーズで既存 pytest スイートを完走させる。
- controller の API 切り出しに合わせて新しいユニットテストを追加し、Textual 依存のないロジック部分を隔離。
- UI リファクタ後は既存 UI テストを更新し、主要キーボード操作（Enter/Shift+Enter、コマンドパレット遷移）を再確認。

## リスクと緩和策
- **大量の差分発生**: フェーズごとに git コミットを細かく分け、docs/experiment.yaml に進捗記録を残す。
- **TTD の崩壊**: 各フェーズで失敗するテスト（仮テスト）を書いてから実装し直す運用を徹底。
- **回帰の見落とし**: UI テストが遅い場合は対象メソッドをピンポイントにスタブ化し、高速フィードバックを維持。

## 次のアクション
1. フェーズ1の詳細タスクブレークダウン（クラス移動手順、公開API定義、状態データクラス仕様）を作成。
2. 既存テストで controller / UI の境界に関わる箇所を列挙し、フェーズ1実施時の影響範囲チェックリストを作る。
3. フェーズ1着手前に `/docs/experiment.yaml` へ計画開始を記録し、完了時に結果を追記する。

