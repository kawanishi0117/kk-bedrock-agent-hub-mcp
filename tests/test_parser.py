"""
レスポンスパーサーのプロパティテスト

**Feature: bedrock-kb-mcp-server, Property 3: レスポンスパースで全フィールドを抽出**
**検証対象: 要件 2.2, 2.3, 2.5**
"""

from hypothesis import given, strategies as st, settings

from src.parser import parse_response
from src.models import Citation, KBResponse


# ロケーション情報を生成するストラテジー
location_strategy = st.fixed_dictionaries({
    "type": st.sampled_from(["S3", "WEB", "CONFLUENCE"]),
    "s3Location": st.fixed_dictionaries({
        "uri": st.text(min_size=1, max_size=100).filter(lambda s: s.strip() != ""),
    }),
})

# スコアを生成するストラテジー（None または 0.0-1.0 の float）
score_strategy = st.one_of(
    st.none(),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)

# 単一の引用参照を生成するストラテジー
citation_ref_strategy = st.fixed_dictionaries({
    "content": st.fixed_dictionaries({
        "text": st.text(min_size=0, max_size=500),
    }),
    "location": location_strategy,
    "score": score_strategy,
})

# 引用グループを生成するストラテジー
citation_group_strategy = st.fixed_dictionaries({
    "retrievedReferences": st.lists(citation_ref_strategy, min_size=0, max_size=5),
})

# 有効な Bedrock API レスポンスを生成するストラテジー
valid_response_strategy = st.fixed_dictionaries({
    "output": st.fixed_dictionaries({
        "text": st.text(min_size=0, max_size=1000),
    }),
    "citations": st.lists(citation_group_strategy, min_size=0, max_size=3),
})


class TestProperty3ResponseParsing:
    """
    **Feature: bedrock-kb-mcp-server, Property 3: レスポンスパースで全フィールドを抽出**
    **検証対象: 要件 2.2, 2.3, 2.5**

    任意の有効な Bedrock RetrieveAndGenerate API レスポンスに対して、
    パース結果は以下を満たす：
    - answer フィールドは API レスポンスの output.text と等しい
    - 各引用は retrievedReferences から抽出された content, location, score を含む
    """

    @given(response=valid_response_strategy)
    @settings(max_examples=100)
    def test_answer_equals_output_text(self, response: dict):
        """
        任意の有効なレスポンスに対して、パース結果の answer は
        元のレスポンスの output.text と等しい。
        """
        result = parse_response(response)

        expected_answer = response["output"]["text"]
        assert result.answer == expected_answer

    @given(response=valid_response_strategy)
    @settings(max_examples=100)
    def test_citations_extracted_from_retrieved_references(self, response: dict):
        """
        任意の有効なレスポンスに対して、パース結果の citations は
        retrievedReferences から正しく抽出される。
        """
        result = parse_response(response)

        # 期待される引用の総数を計算
        expected_count = sum(
            len(group.get("retrievedReferences", []))
            for group in response.get("citations", [])
        )
        assert len(result.citations) == expected_count

    @given(response=valid_response_strategy)
    @settings(max_examples=100)
    def test_citation_fields_match_source(self, response: dict):
        """
        任意の有効なレスポンスに対して、各引用の content, location, score は
        元の retrievedReferences の値と一致する。
        """
        result = parse_response(response)

        # 元のレスポンスから全ての引用参照をフラット化
        expected_refs = []
        for group in response.get("citations", []):
            for ref in group.get("retrievedReferences", []):
                expected_refs.append(ref)

        # 各引用が正しくパースされていることを検証
        assert len(result.citations) == len(expected_refs)

        for citation, ref in zip(result.citations, expected_refs):
            # content の検証
            expected_content = ref.get("content", {}).get("text", "")
            assert citation.content == expected_content

            # location の検証
            expected_location = ref.get("location", {})
            assert citation.location == expected_location

            # score の検証
            expected_score = ref.get("score")
            if expected_score is not None:
                assert citation.score == float(expected_score)
            else:
                assert citation.score is None

    @given(answer_text=st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_empty_citations_returns_empty_list(self, answer_text: str):
        """
        citations が空または存在しない場合、空のリストが返される。
        """
        # citations が空のレスポンス
        response_empty = {"output": {"text": answer_text}, "citations": []}
        result_empty = parse_response(response_empty)
        assert result_empty.citations == []
        assert result_empty.answer == answer_text

        # citations が存在しないレスポンス
        response_missing = {"output": {"text": answer_text}}
        result_missing = parse_response(response_missing)
        assert result_missing.citations == []
        assert result_missing.answer == answer_text
