# 実装計画

## 概要
kk-bedrock-agent-hub-mcp: Amazon Bedrock Knowledge Base から情報を検索する MCP サーバー

**注意:** このサーバーは `Retrieve` API を使用し、`BEDROCK_MODEL_ARN` は不要です。

---

- [x] 1. プロジェクト構造と依存関係のセットアップ







  - ディレクトリ構造を確認: `src/`, `tests/`
  - `pyproject.toml` を更新し、依存関係を確認: `mcp[server]`, `fastmcp`, `boto3`, `pytest`, `hypothesis`, `pytest-mock`
  - _要件: 4.1_

- [x] 2. 設定モジュールの更新（BEDROCK_MODEL_ARN 削除）





  - [x] 2.1 `src/config.py` を更新し、`KBConfig` から `model_arn` を削除


    - `AWS_REGION` を読み込み（デフォルト: `ap-northeast-1`）
    - `BEDROCK_KB_ID` を読み込み（必須）
    - 必須変数が欠落している場合は変数名を含む `ValueError` を発生
    - _要件: 1.1, 1.2, 1.3_
  - [x] 2.2 設定読み込みのプロパティテストを更新


    - **プロパティ 1: 設定値の正確な読み込み**
    - **検証対象: 要件 1.1, 1.2**
  - [x] 2.3 設定欠落エラーのプロパティテストを更新

    - **プロパティ 2: 必須設定欠落時のエラー**
    - **検証対象: 要件 1.3**

- [x] 3. データモデルの更新





  - [x] 3.1 `src/models.py` を更新し、`RetrievalResult` と `KBResponse` データクラスを定義


    - `RetrievalResult`: content, location, score
    - `KBResponse`: results リスト（Retrieve API 用）
    - _要件: 2.2, 2.3, 2.5_

- [x] 4. レスポンスパーサーの更新（Retrieve API 対応）





  - [x] 4.1 `src/parser.py` を更新し、`parse_retrieve_response()` 関数を実装


    - `retrievalResults` から検索結果を抽出
    - 各結果から content, location, score を抽出
    - 欠落/空フィールドを適切に処理
    - _要件: 2.2, 2.3, 2.5_
  - [x] 4.2 レスポンスパースのプロパティテストを更新


    - **プロパティ 3: レスポンスパースで全フィールドを抽出**
    - **検証対象: 要件 2.2, 2.3, 2.5**

- [x] 5. Bedrockクライアントの更新（Retrieve API 対応）





  - [x] 5.1 `src/bedrock_client.py` を更新し、`Retrieve` API を使用


    - `build_retrieve_request()` 関数を実装
    - `query_knowledge_base()` を `Retrieve` API 呼び出しに変更
    - max_results パラメータから `numberOfResults` を設定
    - _要件: 2.1, 2.4_
  - [x] 5.2 リクエスト構築のプロパティテストを更新


    - **プロパティ 4: リクエスト構築で全パラメータを含む**
    - **検証対象: 要件 2.1, 2.4**

- [x] 6. チェックポイント - テスト実行





  - 全テストが通ることを確認し、質問があればユーザーに確認する

- [x] 7. 入力バリデーションの確認





  - [x] 7.1 `src/validation.py` の動作を確認


    - 空文字列を拒否
    - 空白のみの文字列を拒否
    - 成功時はトリム済みクエリを返す
    - _要件: 3.4_
  - [x] 7.2 空白バリデーションのプロパティテストを確認

    - **プロパティ 5: 空白のみのクエリを拒否**
    - **検証対象: 要件 3.4**

- [x] 8. エラーハンドリングの更新





  - [x] 8.1 `src/bedrock_client.py` のエラーハンドリングを確認・更新


    - 認証エラー用の `ClientError` をキャッチ
    - ResourceNotFound 用の `ClientError` をキャッチ
    - 汎用例外をキャッチし詳細を保持
    - _要件: 3.1, 3.2, 3.3_
  - [x] 8.2 エラー詳細保持のプロパティテストを確認


    - **プロパティ 6: APIエラーで例外詳細を保持**
    - **検証対象: 要件 3.3**
  - [x] 8.3 特定エラーシナリオのユニットテストを確認


    - 認証エラーハンドリングのテスト
    - KB未検出エラーハンドリングのテスト
    - _要件: 3.1, 3.2_

- [x] 9. MCPサーバーの更新





  - [x] 9.1 `src/server.py` を更新

    - "kk-bedrock-agent-hub-mcp" という名前で FastMCP を初期化
    - `kb_answer` ツールを Retrieve API 対応に更新
    - レスポンスフォーマットを検索結果用に変更
    - _要件: 2.1, 4.1, 4.2_

  - [x] 9.2 ツールスキーマ登録のユニットテストを更新

    - ツールが正しい名前とパラメータで登録されていることを検証
    - _要件: 4.2_

- [x] 10. ドキュメントの更新






  - [x] 10.1 `README.md` を更新

    - 環境変数を更新（BEDROCK_MODEL_ARN を削除）
    - MCPクライアント設定の例を更新
    - _要件: 1.1, 1.2, 1.4_

- [x] 11. 最終チェックポイント





  - 全テストが通ることを確認し、質問があればユーザーに確認する
