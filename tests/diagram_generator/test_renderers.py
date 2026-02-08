
import pytest
from diagram_generator.graph_model import DiagramGraph, ClassInfo
from diagram_generator.renderers import (
    render_class_diagram,
    render_class_diagram_dot,
    render_dependency_diagram,
    render_call_diagram
)

@pytest.fixture
def sample_graph():
    graph = DiagramGraph()
    # Classes
    graph.classes["A"] = ClassInfo(module="mod1")
    graph.classes["A"].methods.add("foo")
    graph.classes["A"].attributes.add("x")
    
    graph.classes["B"] = ClassInfo(module="mod1")
    graph.classes["C"] = ClassInfo(module="mod2")
    
    # Relations
    graph.inheritance.add(("B", "A")) # B inherits A
    graph.composition.add(("A", "C")) # A composed of C
    graph.usage.add(("B", "C"))       # B uses C
    graph.dependencies.add(("mod1", "mod2"))
    
    return graph

def test_render_class_diagram_mermaid(sample_graph):
    output = render_class_diagram(sample_graph)
    
    assert "classDiagram" in output
    assert "class A {" in output
    assert "+x" in output
    assert "+foo()" in output
    assert "A <|-- B" in output
    assert "A *-- C : composition" in output
    assert "B ..> C : uses" in output

def test_render_class_diagram_dot(sample_graph):
    output = render_class_diagram_dot(sample_graph)
    
    assert "digraph G {" in output
    # Check parts of the node definition to be robust against spacing
    assert '"A" [' in output
    assert 'label="{A|' in output
    # DOT renderer currently doesn't add visibility modifiers logic, just names
    assert 'x\\l' in output
    assert 'foo\\l' in output
    
    assert '"B" -> "A" [arrowhead=empty];' in output # Inheritance
    # Composition: A -> C with diamond on A (tail)
    # The code: "owner" -> "part" [dir=back arrowtail=diamond]
    assert '"A" -> "C" [dir=back arrowtail=diamond' in output

def test_render_dependency_diagram_mermaid(sample_graph):
    output = render_dependency_diagram(sample_graph)
    
    assert "graph TD" in output
    # Internal modules check: mod1 and mod2 are internal because classes use them.
    assert "mod1 --> mod2" in output

def test_render_call_diagram_mermaid(sample_graph):
    # render_call_diagram uses graph.usage in implementation?
    # Let's check implementation:
    # "for src, dst in graph.usage:" -> Yes, it currently uses usage for call diagram?
    # Wait, the code says:
    # def render_call_diagram(graph, ...):
    #    for src, dst in graph.usage: ... 
    # Usually call diagram uses call graph.
    # But let's test based on current implementation.
    
    output = render_call_diagram(sample_graph)
    assert "graph LR" in output
    assert "B --> C" in output

def test_render_class_diagram_focus(sample_graph):
    # Focus only on A and B
    output = render_class_diagram(sample_graph, focus_classes={"A", "B"})
    
    assert "class A {" in output
    assert "class B {" in output
    assert "class C {" not in output
    # Relation A-C (composition) should be excluded since C is hidden
    assert "A *-- C" not in output
    # Relation B-A (inheritance) should be included
    assert "A <|-- B" in output
