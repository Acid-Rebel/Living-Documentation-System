
import pytest
from diagram_generator.graph_model import DiagramGraph, ClassInfo
from diagram_generator.renderers import render_class_diagram_dot

def test_render_composition():
    graph = DiagramGraph()
    # Mock classes so they are visible
    graph.classes["Car"] = ClassInfo(module="test")
    graph.classes["Engine"] = ClassInfo(module="test")
    
    graph.composition.add(("Car", "Engine"))
    graph.multiplicity[("Car", "Engine")] = "1"
    
    dot = render_class_diagram_dot(graph)
    
    # Must have dir=back and arrowtail=diamond
    assert 'dir=back arrowtail=diamond' in dot
    assert 'taillabel="1"' in dot

def test_render_aggregation():
    graph = DiagramGraph()
    graph.classes["Car"] = ClassInfo(module="test")
    graph.classes["Wheel"] = ClassInfo(module="test")
    
    graph.aggregation.add(("Car", "Wheel"))
    graph.multiplicity[("Car", "Wheel")] = "0..*"
    
    dot = render_class_diagram_dot(graph)
    
    assert 'dir=back arrowtail=odiamond' in dot
    assert 'taillabel="0..*"' in dot

def test_render_inheritance():
    graph = DiagramGraph()
    graph.classes["Child"] = ClassInfo(module="test")
    graph.classes["Parent"] = ClassInfo(module="test")
    
    graph.inheritance.add(("Child", "Parent"))
    
    dot = render_class_diagram_dot(graph)
    
    assert '"Child" -> "Parent" [arrowhead=empty];' in dot

from diagram_generator.renderers import render_call_diagram_dot, render_dependency_diagram_dot, render_api_diagram_dot
from api_endpoint_detector.models.api_endpoint import ApiEndpoint

def test_render_call_diagram():
    graph = DiagramGraph()
    graph.classes["A"] = ClassInfo(module="test")
    graph.classes["B"] = ClassInfo(module="test")
    graph.calls.add(("A", "B"))
    
    dot = render_call_diagram_dot(graph)
    assert '"A" -> "B" [style=solid];' in dot

def test_render_dependency_diagram():
    graph = DiagramGraph()
    graph.dependencies.add(("modA", "modB"))
    
    dot = render_dependency_diagram_dot(graph)
    assert '"modA" -> "modB"' in dot

def test_render_api_diagram():
    endpoint = ApiEndpoint(
        path="/api/test",
        http_method="GET",
        handler_name="test_handler",
        class_name="TestController",
        language="python",
        file_path="test.py",
        framework="fastapi"
    )
    endpoints = [endpoint]
    
    
    dot = render_api_diagram_dot(endpoints)
    # Check for controller node and method presence in label
    assert '"TestController"' in dot
    assert 'test_handler' in dot
    assert '/api/test' in dot
