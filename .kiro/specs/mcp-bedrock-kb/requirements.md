# 要件ドキュメント

## はじめに

このドキュメントは、Amazon Bedrock Knowledge Base にクエリを送信する単一のツール（`kb_answer`）を提供するミニマルな MCP（Model Context Protocol）サーバーの要件を定義します。このサーバーにより、AI アシスタント（Claude Desktop、Cursor、Kiro）が Bedrock Agent Runtime の `RetrieveAndGenerate` API を使用して、設定された Knowledge Base から情報を取得できるようになります。

## 用語集

- **MCP Server**: Model Context Protocol を実装したサーバー。AI アシスタントが標準化された通信でツールを呼び出すことを可能にする
- **Knowledge Base (KB)**: 検索拡張生成（RAG）用にインデックス化されたドキュメントを含む Amazon Bedrock Knowledge Base
- **RetrieveAndGenerate API**: Knowledge Base を検索し、基盤モデルを使用して回答を生成する Bedrock Agent Runtime API
- **Citation（引用）**: 回答生成に使用されたソースチャンクを示す参照情報
- **Foundation Model ARN**: 回答合成に使用される生成 AI モデルを識別する Amazon リソース名

## 要件

### 要件 1

**ユーザーストーリー:** 開発者として、AWS 認証情報と Knowledge Base 設定で MCP サーバーを構成したい。これにより、サーバーが特定の Bedrock Knowledge Base に接続できるようになる。

#### 受け入れ基準

1. MCP サーバーが起動するとき、mcp-bedrock-kb は `AWS_REGION` 環境変数から AWS リージョンを読み込む（デフォルト値: `ap-northeast-1`）
2. MCP サーバーが起動するとき、mcp-bedrock-kb は `BEDROCK_KB_ID` 環境変数から Knowledge Base ID を読み込む
3. MCP サーバーが起動するとき、mcp-bedrock-kb は `BEDROCK_MODEL_ARN` 環境変数から基盤モデル ARN を読み込む
4. 必須環境変数（`BEDROCK_KB_ID` または `BEDROCK_MODEL_ARN`）が欠落している場合、mcp-bedrock-kb は欠落している変数名を含む明確なエラーメッセージを発生させる
5. `AWS_PROFILE` 環境変数で AWS 認証情報が設定されている場合、mcp-bedrock-kb はそのプロファイルを認証に使用する

### 要件 2

**ユーザーストーリー:** AI アシスタントユーザーとして、`kb_answer` ツールを通じて Knowledge Base にクエリを送信したい。これにより、インデックス化されたドキュメントからソース引用付きの回答を取得できる。

#### 受け入れ基準

1. ユーザーがクエリ文字列で `kb_answer` ツールを呼び出すとき、mcp-bedrock-kb は設定された Knowledge Base ID とモデル ARN で Bedrock Agent Runtime の `RetrieveAndGenerate` API を呼び出す
2. `RetrieveAndGenerate` API が正常に返されるとき、mcp-bedrock-kb はレスポンスから生成された回答テキストを抽出して返す
3. `RetrieveAndGenerate` API が引用を返すとき、mcp-bedrock-kb はコンテンツテキスト、ロケーション、関連性スコアを含む引用情報を抽出して返す
4. ユーザーが `max_results` パラメータを指定するとき、mcp-bedrock-kb はベクトル検索がその数の結果を返すように設定する（デフォルト: 4）
5. `kb_answer` ツールが完了するとき、mcp-bedrock-kb は回答と引用配列の両方を含む構造化されたレスポンスを返す

### 要件 3

**ユーザーストーリー:** 開発者として、MCP サーバーがエラーを適切に処理してほしい。これにより、クエリが失敗したときに問題を診断できる。

#### 受け入れ基準

1. 認証エラーにより Bedrock API 呼び出しが失敗した場合、mcp-bedrock-kb は認証情報の問題を示すエラーメッセージを返す
2. 無効な Knowledge Base ID により Bedrock API 呼び出しが失敗した場合、mcp-bedrock-kb は KB が見つからないことを示すエラーメッセージを返す
3. ネットワークまたはサービスの問題により Bedrock API 呼び出しが失敗した場合、mcp-bedrock-kb は基礎となる例外の詳細を含むエラーメッセージを返す
4. クエリ文字列が空または空白のみの場合、mcp-bedrock-kb はバリデーションエラーでリクエストを拒否する

### 要件 4

**ユーザーストーリー:** 開発者として、MCP サーバーを stdio トランスポートで実行したい。これにより、様々な MCP クライアントと統合できる。

#### 受け入れ基準

1. サーバースクリプトが直接実行されるとき、mcp-bedrock-kb は MCP 通信用の stdio トランスポートモードで起動する
2. MCP サーバーが実行中のとき、mcp-bedrock-kb はパラメータの説明を含む適切なスキーマドキュメントと共に `kb_answer` ツールを公開する
