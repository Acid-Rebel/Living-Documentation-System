import ast

from code_parser.ast_schema import ASTNode

def normalize_python_ast(node) -> ASTNode:
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=None,
        language="python"
    )

    # ---------- IMPORT ----------
    if isinstance(node, ast.Import):
        for alias in node.names:
            child = ASTNode(
                node_type="Import",
                name=alias.name,
                language="python"
            )
            ast_node.children.append(child)
        return ast_node

    if isinstance(node, ast.ImportFrom):
        child = ASTNode(
            node_type="ImportFrom",
            name=node.module,
            language="python"
        )
        ast_node.children.append(child)
        return ast_node

    # ---------- CLASS BASES ----------
    if isinstance(node, ast.ClassDef):
        ast_node.name = node.name
        ast_node.bases = [
            base.id if isinstance(base, ast.Name) else ast.dump(base)
            for base in node.bases
        ]

    # ---------- DEFAULT ----------
    ast_node.name = getattr(node, "name", None)

    for child in ast.iter_child_nodes(node):
        ast_node.children.append(normalize_python_ast(child))

    return ast_node
