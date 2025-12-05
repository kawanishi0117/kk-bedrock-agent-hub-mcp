"""
レスポンスパーサーモジュール

Bedrock Retrieve API レスポンスをパースする。
"""

from typing import Any

from src.models import RetrievalResult, KBResponse


def parse_retrieve_response(response: dict[str, Any]) -> KBResponse:
    """
    Bedrock Retrieve API レスポンスをパースし、KBResponse を返す。

    API レスポンス構造:
    {
        "retrievalResults": [
            {
                "content": {"text": "ソースチャンク..."},
                "location": {"s3Location": {...}, "type": "S3"},
                "score": 0.85
            }
        ]
    }

    Args:
        response: Bedrock Retrieve API からの生レスポンス辞書

    Returns:
        KBResponse: パース済みの検索結果を含むオブジェクト
    """
    results: list[RetrievalResult] = []

    # retrievalResults から検索結果を抽出
    retrieval_results = response.get("retrievalResults", [])

    if isinstance(retrieval_results, list):
        for item in retrieval_results:
            if not isinstance(item, dict):
                continue

            result = _parse_retrieval_result(item)
            if result is not None:
                results.append(result)

    return KBResponse(results=results)


def _parse_retrieval_result(item: dict[str, Any]) -> RetrievalResult | None:
    """
    単一の検索結果をパースする。

    Args:
        item: retrievalResults 内の単一結果辞書

    Returns:
        RetrievalResult: パース済みの検索結果、または無効な場合は None
    """
    # content.text を抽出（欠落/空フィールドは空文字列）
    content_data = item.get("content", {})
    if isinstance(content_data, dict):
        content = content_data.get("text", "")
    else:
        content = ""

    # location を抽出（辞書全体を保持、欠落時は空辞書）
    location = item.get("location", {})
    if not isinstance(location, dict):
        location = {}

    # score を抽出（存在しない場合は None）
    score = item.get("score")
    if score is not None:
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = None

    return RetrievalResult(content=content, location=location, score=score)
