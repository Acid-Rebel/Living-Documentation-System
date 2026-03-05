import pytest
from core.prompts import RAG_SYSTEM_PROMPT, RAG_TEMPLATE, SIMPLE_CHAT_SYSTEM_PROMPT
from jinja2 import Template

def test_rag_system_prompt_structure():
    assert "You are a code assistant" in RAG_SYSTEM_PROMPT
    assert "MARKDOWN" in RAG_SYSTEM_PROMPT
    assert "FORMATTING RULES" in RAG_SYSTEM_PROMPT

def test_rag_template_rendering():
    template = Template(RAG_TEMPLATE)
    rendered = template.render(
        system_prompt="System Prompt",
        output_format_str="JSON",
        conversation_history={"1": type('obj', (object,), {"user_query": type('obj', (object,), {"query_str": "Hi"}), "assistant_response": type('obj', (object,), {"response_str": "Hello"})})},
        contexts=[{"meta_data": {"file_path": "test.py"}, "text": "print('hello')"}],
        input_str="Final Query"
    )
    assert "System Prompt" in rendered
    assert "JSON" in rendered
    assert "User: Hi" in rendered
    assert "You: Hello" in rendered
    assert "File Path: test.py" in rendered
    assert "print('hello')" in rendered
    assert "Final Query" in rendered

def test_simple_chat_system_prompt_formatting():
    formatted = SIMPLE_CHAT_SYSTEM_PROMPT.format(
        repo_type="github",
        repo_url="https://github.com/user/repo",
        repo_name="user/repo",
        language_name="English"
    )
    assert "github" in formatted
    assert "https://github.com/user/repo" in formatted
    assert "user/repo" in formatted
    assert "English" in formatted
