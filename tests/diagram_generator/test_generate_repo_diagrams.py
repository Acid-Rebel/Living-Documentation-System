
import pytest
from unittest.mock import patch, MagicMock, mock_open
from diagram_generator.generate_repo_diagrams import generate_repo_diagrams

@patch("diagram_generator.generate_repo_diagrams.latest_commit")
@patch("diagram_generator.generate_repo_diagrams.clone_repo")
@patch("diagram_generator.generate_repo_diagrams.scan_repo")
@patch("diagram_generator.generate_repo_diagrams.detect_language")
@patch("diagram_generator.generate_repo_diagrams.get_parser")
@patch("diagram_generator.generate_repo_diagrams.ArtifactStore")
@patch("diagram_generator.generate_repo_diagrams.AnalyzerManager")
@patch("diagram_generator.generate_repo_diagrams.DependencyAnalyzerManager")
@patch("diagram_generator.generate_repo_diagrams.DetectorManager")
@patch("diagram_generator.generate_repo_diagrams.DiagramGraph")
@patch("diagram_generator.generate_repo_diagrams.extract_ast_relations")
@patch("diagram_generator.generate_repo_diagrams.render_class_diagram_dot")
@patch("diagram_generator.generate_repo_diagrams.render_dot_to_png")
@patch("diagram_generator.generate_repo_diagrams.render_dependency_diagram_dot")
@patch("diagram_generator.generate_repo_diagrams.shutil.rmtree")
@patch("os.makedirs")
def test_generate_repo_diagrams_success(
    mock_makedirs,
    mock_rmtree,
    mock_render_dep,
    mock_render_png,
    mock_render_class,
    mock_extract_rels,
    MockGraph,
    MockDetector,
    MockDepAnalyzer,
    MockAnalyzer,
    MockArtifactStore,
    mock_get_parser,
    mock_detect,
    mock_scan,
    mock_clone,
    mock_commit
):
    # Setup mocks
    mock_commit.return_value = "abcdef1"
    # Setup mocks
    mock_extract_rels.return_value = ({}, [])
    mock_scan.return_value = ["file1.py"]
    mock_detect.return_value = "python"
    
    mock_parser = MagicMock()
    mock_get_parser.return_value = mock_parser
    mock_parser.parse.return_value = "ast"
    mock_parser.normalize.return_value = "unified_ast"
    
    # Mock analyzer results
    mock_analyzer_instance = MockAnalyzer.return_value
    mock_analyzer_instance.analyze.return_value = {
        "symbols": [], "relations": []
    }
    
    # Mock artifact store get_artifacts
    mock_store_instance = MockArtifactStore.return_value
    mock_artifacts = MagicMock()
    mock_artifacts.relations = [] # Empty list for loop
    mock_artifacts.api_endpoints = []
    mock_store_instance.get_artifacts.return_value = mock_artifacts
    
    # Mock dependency analyzer
    MockDepAnalyzer.return_value.analyze.return_value = []
    
    # Mock graph
    mock_graph_instance = MockGraph.return_value
    mock_graph_instance.classes = {} # Empty dict for loop
    
    # Mock file open
    with patch("builtins.open", mock_open(read_data="code")) as mock_file:
        generate_repo_diagrams("https://github.com/user/repo")
        
        # Verify clone called
        mock_clone.assert_called()
        
        # Verify processing
        mock_detect.assert_called()
        mock_get_parser.assert_called()
        mock_parser.parse.assert_called()
        
        # Verify analysis
        mock_analyzer_instance.analyze.assert_called()
        
        # Verify rendering called
        mock_render_class.assert_called()
        mock_render_dep.assert_called()
        mock_render_png.assert_called()

def test_repo_name_extraction():
    # Only import the function or duplicate logic?
    # It is a top-level function in generate_repo_diagrams.py, but not exported in __all__ maybe.
    from diagram_generator.generate_repo_diagrams import repo_name_from_url
    assert repo_name_from_url("https://github.com/a/b.git") == "b"
    assert repo_name_from_url("https://github.com/a/b") == "b"
