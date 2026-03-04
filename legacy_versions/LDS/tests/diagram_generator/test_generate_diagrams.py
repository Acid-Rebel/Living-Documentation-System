
import pytest
from unittest.mock import patch, mock_open, MagicMock
from diagram_generator.generate_diagrams import generate_diagrams

@patch("diagram_generator.generate_diagrams.detect_language")
@patch("diagram_generator.generate_diagrams.get_parser")
@patch("diagram_generator.generate_diagrams.traverse")
@patch("diagram_generator.generate_diagrams.render_class_diagram")
@patch("diagram_generator.generate_diagrams.render_dependency_diagram")
@patch("diagram_generator.generate_diagrams.render_call_diagram")
@patch("os.makedirs")
def test_generate_diagrams_flow(
    mock_makedirs,
    mock_render_call,
    mock_render_dep,
    mock_render_class,
    mock_traverse,
    mock_get_parser,
    mock_detect,
):
    # Setup
    mock_detect.return_value = "python"
    mock_parser = MagicMock()
    mock_get_parser.return_value = mock_parser
    mock_parser.parse.return_value = "raw_ast"
    mock_parser.normalize.return_value = "unified_ast"
    
    mock_render_class.return_value = "class_diagram_content"
    mock_render_dep.return_value = "dep_diagram_content"
    mock_render_call.return_value = "call_diagram_content"

    # Mock file open
    with patch("builtins.open", mock_open(read_data="source_code")) as mock_file:
        generate_diagrams("test_file.py")
        
        # Verify read
        mock_file.assert_any_call("test_file.py", "r")
        
        # Verify parsing
        mock_parser.parse.assert_called_with("source_code")
        mock_parser.normalize.assert_called_with("raw_ast")
        
        # Verify traversal
        mock_traverse.assert_called()
        
        # Verify writes
        handle = mock_file()
        handle.write.assert_any_call("class_diagram_content")
        handle.write.assert_any_call("dep_diagram_content")
        handle.write.assert_any_call("call_diagram_content")
