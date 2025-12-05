"""
設定モジュール

環境変数から Bedrock Knowledge Base の設定を読み込む。
Retrieve API を使用するため、基盤モデル ARN は不要。
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KBConfig:
    """
    Bedrock Knowledge Base の設定を保持するデータクラス。
    
    Attributes:
        aws_region: AWS リージョン
        kb_id: Knowledge Base ID
    """
    aws_region: str
    kb_id: str


def load_config() -> KBConfig:
    """
    環境変数から設定を読み込み、KBConfig インスタンスを返す。
    
    環境変数:
        AWS_REGION: AWS リージョン（デフォルト: ap-northeast-1）
        BEDROCK_KB_ID: Knowledge Base ID（必須）
    
    Returns:
        KBConfig: 設定値を含むデータクラスインスタンス
    
    Raises:
        ValueError: 必須の環境変数が設定されていない場合
    """
    # 必須変数のチェック（BEDROCK_KB_ID のみ必須）
    kb_id = os.environ.get("BEDROCK_KB_ID")
    if not kb_id:
        raise ValueError(
            "必須の環境変数が設定されていません: BEDROCK_KB_ID"
        )
    
    # AWS_REGION はデフォルト値あり
    aws_region = os.environ.get("AWS_REGION", "ap-northeast-1")
    
    return KBConfig(
        aws_region=aws_region,
        kb_id=kb_id,
    )
