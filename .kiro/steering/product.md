# Product Overview

Amazon Bedrock Knowledge Base にクエリを送信する MCP (Model Context Protocol) サーバー。

## 目的

AI アシスタント（Claude Desktop、Cursor、Kiro）が Amazon Bedrock Knowledge Base から情報を取得できるようにする `kb_answer` ツールを提供する。

## 主要機能

- Bedrock RetrieveAndGenerate API を使用した Knowledge Base クエリ
- 環境変数ベースの設定管理
- 引用情報（ソース、スコア）の抽出と返却
- 入力バリデーション

## 対象ユーザー

- MCP 対応の AI アシスタントを使用する開発者
- AWS Bedrock Knowledge Base を活用したい組織
