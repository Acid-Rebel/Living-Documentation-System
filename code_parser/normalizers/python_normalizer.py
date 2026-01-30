import ast

from code_parser.ast_schema import ASTNode

def normalize_python_ast(node) -> ASTNode:
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=getattr(node, 'name', None),
        language="python",
    )

    # ✅ Preserve call targets
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            ast_node.call_target = node.func.id
        elif isinstance(node.func, ast.Attribute):
            ast_node.call_target = node.func.attr

    # ✅ Preserve class bases
    if isinstance(node, ast.ClassDef):
        ast_node.bases = [b.id if hasattr(b, "id") else str(b) for b in node.bases]

    for child in ast.iter_child_nodes(node):
        ast_node.children.append(normalize_python_ast(child))

    return ast_node
