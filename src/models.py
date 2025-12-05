"""
データモデルモジュール

Bedrock Knowledge Base Retrieve API レスポンスのデータクラスを定義。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievalResult:
    """
    Knowledge Base からの検索結果を保持するデータクラス。
    
    Retrieve API の retrievalResults から抽出された情報を格納。
    
    Attributes:
        content: 検索されたテキストコンテンツ
        location: ソースの場所情報（S3 ロケーションなど）
        score: 関連性スコア（存在しない場合は None）
    """
    content: str
    location: dict[str, Any]
    score: float | None = None


# 後方互換性のためのエイリアス
Citation = RetrievalResult


@dataclass(frozen=True)
class KBResponse:
    """
    Knowledge Base Retrieve API のレスポンスを保持するデータクラス。
    
    Retrieve API は検索結果のリストのみを返す（回答生成なし）。
    
    Attributes:
        results: 検索結果（RetrievalResult）のリスト
        
    Note:
        answer と citations は後方互換性のために残されています。
        タスク 4 でパーサーが更新された後に削除予定。
    """
    # Retrieve API 用の新しいフィールド
    results: list[RetrievalResult] = field(default_factory=list)
    
    # 後方互換性のためのフィールド（タスク 4 完了後に削除予定）
    answer: str = ""
    citations: list[RetrievalResult] = field(default_factory=list)
