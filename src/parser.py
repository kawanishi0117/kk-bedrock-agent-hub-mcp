"""
レスポンスパーサーモジュール

Bedrock RetrieveAndGenerate API レスポンスをパースする。
"""

from typing import Any

from src.models import Citation, KBResponse


def parse_response(response: dict[str, Any]) -> KBResponse:
    """
    Bedrock RetrieveAndGenerate API レスポンスをパースし、KBResponse を返す。
    
    API レスポンス構造:
    {
        "output": {"text": "生成された回答..."},
        "citations": [
            {
                "retrievedReferences": [
                    {
                        "content": {"text": "ソースチャンク..."},
                        "location": {"s3Location": {...}, "type": "S3"},
                        "score": 0.85
                    }
                ]
            }
        ]
    }
    
    Args:
        response: Bedrock API からの生レスポンス辞書
    
    Returns:
        KBResponse: パース済みの回答と引用を含むオブジェクト
    """
    # output.text から回答を抽出（欠落時は空文字列）
    output = response.get("output", {})
    answer = output.get("text", "") if isinstance(output, dict) else ""
    
    # citations から引用情報を抽出
    citations: list[Citation] = []
    citations_data = response.get("citations", [])
    
    if isinstance(citations_data, list):
        for citation_group in citations_data:
            if not isinstance(citation_group, dict):
                continue
            
            # retrievedReferences から各引用を抽出
            retrieved_refs = citation_group.get("retrievedReferences", [])
            if not isinstance(retrieved_refs, list):
                continue
            
            for ref in retrieved_refs:
                if not isinstance(ref, dict):
                    continue
                
                citation = _parse_citation(ref)
                if citation is not None:
                    citations.append(citation)
    
    return KBResponse(answer=answer, citations=citations)


def _parse_citation(ref: dict[str, Any]) -> Citation | None:
    """
    単一の引用参照をパースする。
    
    Args:
        ref: retrievedReferences 内の単一参照辞書
    
    Returns:
        Citation: パース済みの引用、または無効な場合は None
    """
    # content.text を抽出
    content_data = ref.get("content", {})
    if isinstance(content_data, dict):
        content = content_data.get("text", "")
    else:
        content = ""
    
    # location を抽出（辞書全体を保持）
    location = ref.get("location", {})
    if not isinstance(location, dict):
        location = {}
    
    # score を抽出（存在しない場合は None）
    score = ref.get("score")
    if score is not None:
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = None
    
    return Citation(content=content, location=location, score=score)
