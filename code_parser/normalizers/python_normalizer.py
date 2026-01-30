import ast
from typing import Any, Dict, List, Optional

from code_parser.ast_schema import ASTNode


def normalize_python_ast(node: ast.AST) -> ASTNode:
    metadata = _extract_metadata(node)
    node_name = _resolve_node_name(node)
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=node_name,
        language="python",
        metadata=metadata,
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


def _extract_metadata(node: ast.AST) -> Optional[Dict[str, Any]]:
    metadata: Dict[str, Any] = {}

    decorator_list = getattr(node, "decorator_list", None)
    if decorator_list:
        decorators: List[Dict[str, Any]] = []
        for decorator in decorator_list:
            serialized = _serialize_decorator(decorator)
            if serialized:
                decorators.append(serialized)
        if decorators:
            metadata["decorators"] = decorators

    if isinstance(node, ast.Constant):
        metadata["value"] = node.value
    elif isinstance(node, ast.Name):
        metadata["id"] = node.id
        metadata["ctx"] = type(node.ctx).__name__ if hasattr(node, "ctx") else None
    elif isinstance(node, ast.Attribute):
        metadata["attr"] = node.attr
        resolved = _resolve_name(node)
        if resolved:
            metadata["value"] = resolved
    elif isinstance(node, ast.keyword):
        metadata["arg"] = node.arg
    elif isinstance(node, ast.Call):
        func_name = _resolve_name(node.func)
        if func_name:
            metadata["func"] = func_name

    return metadata or None


def _serialize_decorator(decorator: ast.AST) -> Optional[Dict[str, Any]]:
    if isinstance(decorator, ast.Call):
        name = _resolve_name(decorator.func)
        args = [_literal_value(arg) for arg in decorator.args]
        keywords = {
            kw.arg: _literal_value(kw.value)
            for kw in decorator.keywords
            if kw.arg is not None
        }
        return {
            "name": name,
            "args": args,
            "keywords": keywords,
        }

    name = _resolve_name(decorator)
    if name:
        return {"name": name}
    return None


def _resolve_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Attribute):
        parts: List[str] = []
        current: Optional[ast.AST] = node
        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.insert(0, current.id)
        return ".".join(parts) if parts else None
    if isinstance(node, ast.Name):
        return node.id
    return None


def _resolve_node_name(node: ast.AST) -> Optional[str]:
    direct_name = getattr(node, "name", None)
    if direct_name:
        return direct_name
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.alias):
        return node.name
    if isinstance(node, ast.keyword):
        return node.arg
    return None


def _literal_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [_literal_value(element) for element in node.elts]
    if isinstance(node, ast.Dict):
        return {
            _literal_value(key): _literal_value(value)
            for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _resolve_name(node)
    return None
