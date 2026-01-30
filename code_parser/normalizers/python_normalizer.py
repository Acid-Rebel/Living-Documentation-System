import ast

from code_parser.ast_schema import ASTNode

def normalize_python_ast(node) -> ASTNode:
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=getattr(node, 'name', None),
        language='python'
    )
    for child in ast.iter_child_nodes(node):
        ast_node.children.append(normalize_python_ast(child))
    return ast_node
