
import pytest
import os
import shutil
from diagram_generator.renderers import render_dot_to_png

# Helper to check if graphviz is installed
def is_graphviz_installed():
    if shutil.which("dot"):
        return True
    
    # Common Windows install path check used in renderers.py
    if os.name == 'nt':
        common_path = r"C:\Program Files\Graphviz\bin"
        if os.path.exists(common_path) and os.path.exists(os.path.join(common_path, "dot.exe")):
            return True
            
    return False

@pytest.mark.skipif(not is_graphviz_installed(), reason="Graphviz (dot) executable not found.")
def test_render_dot_to_png_creates_file(tmp_path):
    """
    Integration test: Verifies that render_dot_to_png actually creates a file on disk.
    Requires Graphviz installed on the system.
    """
    # Simple DOT content
    dot_content = 'digraph G { "A" -> "B"; }'
    
    # Use tmp_path fixture for safe file creation
    output_png = tmp_path / "test_diagram.png"
    output_png_str = str(output_png)
    
    # Run renderer
    try:
        render_dot_to_png(dot_content, output_png_str)
    except Exception as e:
        pytest.fail(f"render_dot_to_png failed with error: {e}")
    
    # Verify file exists
    assert os.path.exists(output_png_str), "PNG file was not created"
    assert os.path.getsize(output_png_str) > 0, "PNG file is empty"
