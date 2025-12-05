"""
入力バリデーションモジュール

クエリ文字列のバリデーションを担当する。
"""


class ValidationError(ValueError):
    """
    バリデーションエラーを表す例外クラス。
    
    入力値が不正な場合に発生する。
    """


def validate_query(query: str) -> str:
    """
    クエリ文字列をバリデーションし、トリム済みの文字列を返す。
    
    Args:
        query: バリデーション対象のクエリ文字列
    
    Returns:
        str: トリム済みのクエリ文字列
    
    Raises:
        ValidationError: クエリが空文字列または空白のみの場合
    
    Examples:
        >>> validate_query("  hello world  ")
        'hello world'
        >>> validate_query("")
        Traceback (most recent call last):
            ...
        ValidationError: クエリ文字列が空です
    """
    # None チェック
    if query is None:
        raise ValidationError("クエリ文字列が空です")
    
    # トリム処理
    trimmed = query.strip()
    
    # 空文字列チェック
    if not trimmed:
        raise ValidationError("クエリ文字列が空です")
    
    return trimmed
