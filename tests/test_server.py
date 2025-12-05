"""
MCP サーバーのユニットテスト

ツールスキーマ登録の検証を行う。
"""

import pytest

from src.server import mcp


class TestToolRegistration:
    """
    ツール登録のテストクラス。
    
    要件 4.2: ツールが正しい名前とパラメータで登録されていることを検証
    """
    
    def test_mcp_server_name(self):
        """MCP サーバーが正しい名前で初期化されていることを検証"""
        assert mcp.name == "bedrock-kb-mcp"
    
    def test_kb_answer_tool_registered(self):
        """kb_answer ツールが登録されていることを検証"""
        # FastMCP の内部ツールリストを確認（_tools 属性を使用）
        tool_names = [tool.name for tool in mcp._tool_manager._tools.values()]
        assert "kb_answer" in tool_names
    
    def test_kb_answer_tool_parameters(self):
        """kb_answer ツールのパラメータが正しく定義されていることを検証"""
        # ツールを取得
        tools = mcp._tool_manager._tools
        kb_answer_tool = None
        for tool in tools.values():
            if tool.name == "kb_answer":
                kb_answer_tool = tool
                break
        
        assert kb_answer_tool is not None
        
        # パラメータスキーマを検証
        schema = kb_answer_tool.parameters
        properties = schema.get("properties", {})
        
        # query パラメータの存在確認
        assert "query" in properties
        assert properties["query"]["type"] == "string"
        
        # max_results パラメータの存在確認
        assert "max_results" in properties
        assert properties["max_results"]["type"] == "integer"
    
    def test_kb_answer_required_parameters(self):
        """kb_answer ツールの必須パラメータが正しく定義されていることを検証"""
        tools = mcp._tool_manager._tools
        kb_answer_tool = None
        for tool in tools.values():
            if tool.name == "kb_answer":
                kb_answer_tool = tool
                break
        
        assert kb_answer_tool is not None
        
        # 必須パラメータを検証
        schema = kb_answer_tool.parameters
        required = schema.get("required", [])
        
        # query は必須
        assert "query" in required
        # max_results はデフォルト値があるため必須ではない
        assert "max_results" not in required


class TestKbAnswerFunction:
    """
    kb_answer 関数の基本動作テスト。
    
    実際の API 呼び出しは行わず、入力バリデーションのみテスト。
    """
    
    def test_empty_query_returns_error(self):
        """空のクエリがエラーメッセージを返すことを検証"""
        # FastMCP のツールは FunctionTool オブジェクトなので、fn 属性で関数を取得
        tools = mcp._tool_manager._tools
        kb_answer_tool = None
        for tool in tools.values():
            if tool.name == "kb_answer":
                kb_answer_tool = tool
                break
        
        assert kb_answer_tool is not None
        result = kb_answer_tool.fn(query="")
        assert "エラー" in result
    
    def test_whitespace_query_returns_error(self):
        """空白のみのクエリがエラーメッセージを返すことを検証"""
        tools = mcp._tool_manager._tools
        kb_answer_tool = None
        for tool in tools.values():
            if tool.name == "kb_answer":
                kb_answer_tool = tool
                break
        
        assert kb_answer_tool is not None
        result = kb_answer_tool.fn(query="   ")
        assert "エラー" in result
