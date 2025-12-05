# 要件ドキュメント

## はじめに

このドキュメントは、Amazon Bedrock Knowledge Base から情報を取得する単一のツール（`kb_answer`）を提供するミニマルな MCP（Model Context Protocol）サーバーの要件を定義します。このサーバーにより、AI アシスタント（Claude Desktop、Cursor、Kiro）が Bedrock Agent Runtime の `Retrieve` API を使用して、設定された Knowledge Base からドキュメントチャンクを検索・取得できるようになります。

**注意:** このサーバーは回答生成（RetrieveAndGenerate）ではなく、純粋な検索（Retrieve）機能のみを提供します。基盤モデル ARN は不要です。

## 用語集

- **kk-bedrock-agent-hub-mcp**: 本システムの名称。Amazon Bedrock Knowledge Base への検索機能を MCP 経由で提供する
- **MCP Server**: Model Context Protocol を実装したサーバー。AI アシスタントが標準化された通信でツールを呼び出すことを可能にする
- **Knowledge Base (KB)**: 検索拡張生成（RAG）用にインデックス化されたドキュメントを含む Amazon Bedrock Knowledge Base
- **Retrieve API**: Knowledge Base からクエリに関連するドキュメントチャンクを検索・取得する Bedrock Agent Runtime API
- **Citation（引用）**: 検索結果として返されるソースチャンクの参照情報（コンテンツ、ロケーション、スコア）

## 要件

### 要件 1

**ユーザーストーリー:** 開発者として、AWS 認証情報と Knowledge Base 設定で MCP サーバーを構成したい。これにより、サーバーが特定の Bedrock Knowledge Base に接続できるようになる。

#### 受け入れ基準

1. MCP サーバーが起動するとき、kk-bedrock-agent-hub-mcp は `AWS_REGION` 環境変数から AWS リージョンを読み込む（デフォルト値: `ap-northeast-1`）
2. MCP サーバーが起動するとき、kk-bedrock-agent-hub-mcp は `BEDROCK_KB_ID` 環境変数から Knowledge Base ID を読み込む
3. 必須環境変数（`BEDROCK_KB_ID`）が欠落している場合、kk-bedrock-agent-hub-mcp は欠落している変数名を含む明確なエラーメッセージを発生させる
4. `AWS_PROFILE` 環境変数で AWS 認証情報が設定されている場合、kk-bedrock-agent-hub-mcp はそのプロファイルを認証に使用する

### 要件 2

**ユーザーストーリー:** AI アシスタントユーザーとして、`kb_answer` ツールを通じて Knowledge Base にクエリを送信したい。これにより、インデックス化されたドキュメントから関連するチャンクを取得できる。

#### 受け入れ基準

1. ユーザーがクエリ文字列で `kb_answer` ツールを呼び出すとき、kk-bedrock-agent-hub-mcp は設定された Knowledge Base ID で Bedrock Agent Runtime の `Retrieve` API を呼び出す
2. `Retrieve` API が正常に返されるとき、kk-bedrock-agent-hub-mcp はレスポンスから検索結果（retrievalResults）を抽出して返す
3. `Retrieve` API が検索結果を返すとき、kk-bedrock-agent-hub-mcp は各結果からコンテンツテキスト、ロケーション、関連性スコアを含む情報を抽出して返す
4. ユーザーが `max_results` パラメータを指定するとき、kk-bedrock-agent-hub-mcp はベクトル検索がその数の結果を返すように設定する（デフォルト: 4）
5. `kb_answer` ツールが完了するとき、kk-bedrock-agent-hub-mcp は検索結果の配列を含む構造化されたレスポンスを返す

### 要件 3

**ユーザーストーリー:** 開発者として、MCP サーバーがエラーを適切に処理してほしい。これにより、クエリが失敗したときに問題を診断できる。

#### 受け入れ基準

1. 認証エラーにより Bedrock API 呼び出しが失敗した場合、kk-bedrock-agent-hub-mcp は認証情報の問題を示すエラーメッセージを返す
2. 無効な Knowledge Base ID により Bedrock API 呼び出しが失敗した場合、kk-bedrock-agent-hub-mcp は KB が見つからないことを示すエラーメッセージを返す
3. ネットワークまたはサービスの問題により Bedrock API 呼び出しが失敗した場合、kk-bedrock-agent-hub-mcp は基礎となる例外の詳細を含むエラーメッセージを返す
4. クエリ文字列が空または空白のみの場合、kk-bedrock-agent-hub-mcp はバリデーションエラーでリクエストを拒否する

### 要件 4

**ユーザーストーリー:** 開発者として、MCP サーバーを stdio トランスポートで実行したい。これにより、様々な MCP クライアントと統合できる。

#### 受け入れ基準

1. サーバースクリプトが直接実行されるとき、kk-bedrock-agent-hub-mcp は MCP 通信用の stdio トランスポートモードで起動する
2. MCP サーバーが実行中のとき、kk-bedrock-agent-hub-mcp はパラメータの説明を含む適切なスキーマドキュメントと共に `kb_answer` ツールを公開する
