"""
設定モジュールのプロパティテスト

**Feature: kk-bedrock-agent-hub-mcp, Property 1: 設定値の正確な読み込み**
**Feature: kk-bedrock-agent-hub-mcp, Property 2: 必須設定欠落時のエラー**
"""

import os
from contextlib import contextmanager

import pytest
from hypothesis import given, strategies as st, settings

from src.config import load_config


@contextmanager
def env_vars(**kwargs):
    """
    テスト用に環境変数を一時的に設定するコンテキストマネージャー。
    コンテキスト終了時に元の状態に復元する。
    """
    # 元の値を保存
    original = {}
    vars_to_delete = []
    
    for key, value in kwargs.items():
        if key in os.environ:
            original[key] = os.environ[key]
        else:
            vars_to_delete.append(key)
        
        if value is None:
            # None の場合は環境変数を削除
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    
    try:
        yield
    finally:
        # 元の状態に復元
        for key in vars_to_delete:
            os.environ.pop(key, None)
        for key, value in original.items():
            os.environ[key] = value


# 有効な設定値を生成するストラテジー
# 空文字列や空白のみは除外、ASCII文字のみ
valid_string = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        whitelist_characters="-_"
    ),
    min_size=1,
    max_size=100
).filter(lambda s: s.strip() != "")

# AWS リージョン形式の文字列
aws_region_strategy = st.sampled_from([
    "ap-northeast-1",
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-southeast-1",
])


class TestProperty1ConfigLoading:
    """
    **Feature: kk-bedrock-agent-hub-mcp, Property 1: 設定値の正確な読み込み**
    **検証対象: 要件 1.1, 1.2**
    
    任意の有効な AWS_REGION と BEDROCK_KB_ID の環境変数値に対して、
    load_config() はそれらの値を正確に含む KBConfig を返す。
    AWS_REGION が設定されていない場合、デフォルト値 'ap-northeast-1' が使用される。
    """

    @given(
        kb_id=valid_string,
        aws_region=aws_region_strategy,
    )
    @settings(max_examples=100)
    def test_config_loads_all_values_correctly(
        self, kb_id: str, aws_region: str
    ):
        """
        任意の有効な環境変数値に対して、load_config() は
        それらの値を正確に KBConfig に格納する。
        """
        with env_vars(
            BEDROCK_KB_ID=kb_id,
            AWS_REGION=aws_region
        ):
            config = load_config()
            
            # 全ての値が正確に読み込まれていることを検証
            assert config.kb_id == kb_id
            assert config.aws_region == aws_region

    @given(kb_id=valid_string)
    @settings(max_examples=100)
    def test_config_uses_default_region_when_not_set(self, kb_id: str):
        """
        AWS_REGION が設定されていない場合、デフォルト値
        'ap-northeast-1' が使用される。
        """
        with env_vars(
            BEDROCK_KB_ID=kb_id,
            AWS_REGION=None  # 削除
        ):
            config = load_config()
            
            # デフォルトリージョンが使用されていることを検証
            assert config.aws_region == "ap-northeast-1"
            assert config.kb_id == kb_id


class TestProperty2MissingConfigError:
    """
    **Feature: kk-bedrock-agent-hub-mcp, Property 2: 必須設定欠落時のエラー**
    **検証対象: 要件 1.3**
    
    BEDROCK_KB_ID が欠落している環境状態に対して、load_config() を呼び出すと、
    欠落している変数名を含むエラーが発生する。
    """

    @given(aws_region=st.one_of(st.none(), aws_region_strategy))
    @settings(max_examples=100)
    def test_missing_kb_id_raises_error_with_var_name(self, aws_region):
        """
        BEDROCK_KB_ID が欠落している場合、ValueError が発生し、
        エラーメッセージに変数名 'BEDROCK_KB_ID' が含まれる。
        """
        with env_vars(
            BEDROCK_KB_ID=None,
            AWS_REGION=aws_region
        ):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            
            error_message = str(exc_info.value)
            
            # 欠落している変数名がエラーメッセージに含まれることを検証
            assert "BEDROCK_KB_ID" in error_message

    def test_missing_kb_id_shows_var_name_in_error(self):
        """
        BEDROCK_KB_ID が欠落している場合、変数名がエラーメッセージに含まれる。
        """
        with env_vars(
            BEDROCK_KB_ID=None,
            AWS_REGION=None
        ):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            
            error_message = str(exc_info.value)
            assert "BEDROCK_KB_ID" in error_message
