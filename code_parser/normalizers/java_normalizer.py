import javalang

from code_parser.ast_schema import ASTNode


def normalize_java_ast(node) -> ASTNode:
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=getattr(node, "name", None),
        language="java",
    )
    for child in _iter_child_nodes(node):
        ast_node.children.append(normalize_java_ast(child))
    return ast_node


def _iter_child_nodes(node):
    if not isinstance(node, javalang.tree.Node):
        return []

    for child in node.children:
        if isinstance(child, javalang.tree.Node):
            yield child
        elif isinstance(child, (list, tuple)):
            for entry in child:
                if isinstance(entry, javalang.tree.Node):
                    yield entry
