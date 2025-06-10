import os
import sys
import tempfile
import shutil
import pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import generate_problem_via_api

def test_get_context_text(tmp_path, monkeypatch):
    # Patch __file__ to simulate script location
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    context_file = tmp_path / "context"
    context_file.write_text("Test context content.")
    monkeypatch.setattr(generate_problem_via_api, "__file__", str(script_dir / "dummy.py"))
    # Place context file in the expected location (../context relative to script)
    shutil.move(str(context_file), str(tmp_path / "context"))
    # Should read the context file
    assert generate_problem_via_api.get_context_text() == "Test context content."
    # Remove context file, should return ''
    os.remove(str(tmp_path / "context"))
    assert generate_problem_via_api.get_context_text() == ''

def test_extract_question_and_solution():
    # Standard case
    latex = r"""\question What is 2+2?\begin{solution}4\end{solution}"""
    q, s = generate_problem_via_api.extract_question_and_solution(latex)
    assert q.startswith("\\question")
    assert s == "4"
    # With 'Solution:'
    latex = r"\question What is 2+2? Solution: 4"
    q, s = generate_problem_via_api.extract_question_and_solution(latex)
    assert q.startswith("\\question")
    assert s == "4"
    # No solution
    latex = r"\question What is 2+2?"
    q, s = generate_problem_via_api.extract_question_and_solution(latex)
    assert q.startswith("\\question")
    assert s == "<solution here>"

def test_get_next_problem_number(tmp_path):
    # Create fake problem files
    os.makedirs(tmp_path, exist_ok=True)
    for i in [1, 2, 5]:
        (tmp_path / f"problem{i}.tex").write_text("test")
    n = generate_problem_via_api.get_next_problem_number(str(tmp_path))
    assert n == 6
    # No files
    shutil.rmtree(tmp_path)
    os.makedirs(tmp_path, exist_ok=True)
    n = generate_problem_via_api.get_next_problem_number(str(tmp_path))
    assert n == 1
