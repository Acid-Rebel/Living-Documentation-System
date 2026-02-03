
import pytest
from diagram_generator.graph_model import DiagramGraph

def test_add_inheritance():
    graph = DiagramGraph()
    # (Child, Parent, Type, Multiplicity)
    relations = [("Child", "Parent", "INHERITS", None)]
    classes = {
        "Child": {"module": "test", "methods": set(), "attributes": set()},
        "Parent": {"module": "test", "methods": set(), "attributes": set()}
    }
    
    graph.add_ast_relations(classes, relations)
    assert ("Child", "Parent") in graph.inheritance

def test_add_composition_aggregation():
    graph = DiagramGraph()
    relations = [
        ("Car", "Engine", "COMPOSITION", "1"),
        ("Car", "Wheel", "AGGREGATION", "0..*")
    ]
    classes = {
        "Car": {"module": "test", "methods": set(), "attributes": set()},
        "Engine": {"module": "test", "methods": set(), "attributes": set()},
        "Wheel": {"module": "test", "methods": set(), "attributes": set()}
    }
    
    graph.add_ast_relations(classes, relations)
    
    assert ("Car", "Engine") in graph.composition
    assert ("Car", "Wheel") in graph.aggregation
    assert graph.multiplicity[("Car", "Engine")] == "1"
    assert graph.multiplicity[("Car", "Wheel")] == "0..*"

def test_filter_self_calls():
    # Setup: Class A has method 'foo'. A calls A.foo() -> Self call
    graph = DiagramGraph()
    classes = {
        "A": {"methods": {"foo"}, "attributes": set(), "module": "test"}
    }
    
    relations = [("A", "foo", "CALLS", None)]
    
    graph.add_ast_relations(classes, relations)
    
    assert ("A", "foo") not in graph.calls

def test_valid_call():
    graph = DiagramGraph()
    classes = {
        "A": {"methods": set(), "attributes": set(), "module": "test"},
        "B": {"methods": set(), "attributes": set(), "module": "test"}
    }
    relations = [("A", "B", "CALLS", None)]
    
    graph.add_ast_relations(classes, relations)
    assert ("A", "B") in graph.calls
