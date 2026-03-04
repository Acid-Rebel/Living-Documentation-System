
import pytest
from diagram_generator.ast_traverser import traverse
from diagram_generator.graph_model import DiagramGraph
from code_parser.ast_schema import ASTNode

def test_traverse_classes_methods():
    # Setup simple manual AST
    root = ASTNode(node_type="Module", language="python", name="mod")
    cls = ASTNode(node_type="ClassDef", language="python", name="MyClass")
    root.children.append(cls)
    method = ASTNode(node_type="FunctionDef", language="python", name="my_method")
    cls.children.append(method)
    
    graph = DiagramGraph()
    traverse(root, graph, module="test_mod")
    
    assert "MyClass" in graph.classes
    assert "my_method" in graph.classes["MyClass"].methods
    assert graph.classes["MyClass"].module == "test_mod"

def test_traverse_inheritance():
    # MyClass(Parent)
    root = ASTNode(node_type="Module", language="python", name="mod")
    cls = ASTNode(node_type="ClassDef", language="python", name="Child")
    setattr(cls, "bases", ["Parent"])
    root.children.append(cls)
    
    graph = DiagramGraph()
    traverse(root, graph)
    
    assert ("Parent", "Child") in graph.inheritance

def test_traverse_imports():
    root = ASTNode(node_type="Module", language="python", name="mod")
    imp = ASTNode(node_type="Import", language="python", name="requests")
    root.children.append(imp)
    
    graph = DiagramGraph()
    traverse(root, graph, module="myproject.main")
    
    # Dependency: myproject -> requests
    assert ("myproject", "requests") in graph.dependencies
