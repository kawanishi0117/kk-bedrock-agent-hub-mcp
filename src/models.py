"""
データモデルモジュール

Bedrock Knowledge Base レスポンスのデータクラスを定義。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Citation:
    """
    Knowledge Base からの引用情報を保持するデータクラス。
    
    Attributes:
        content: 引用されたテキストコンテンツ
        location: ソースの場所情報（S3 ロケーションなど）
        score: 関連性スコア（存在しない場合は None）
    """
    content: str
    location: dict[str, Any]
    score: float | None = None


@dataclass(frozen=True)
class KBResponse:
    """
    Knowledge Base クエリのレスポンスを保持するデータクラス。
    
    Attributes:
        answer: 生成された回答テキスト
        citations: 引用情報のリスト
    """
    answer: str
    citations: list[Citation] = field(default_factory=list)
