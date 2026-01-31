# Assuming imports are similar
from ..ast_schema import ASTNode
import javalang

def normalize_java_ast(node) -> ASTNode:
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name = getattr(node,'name',None),
        language='java'
    )
    for _,child in node.filter(javalang.tree.Node):
        ast_node.children.append(normalize_java_ast(child))
    return ast_node
 