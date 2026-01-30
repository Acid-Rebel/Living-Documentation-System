import javalang

from code_parser.ast_schema import ASTNode


def normalize_java_ast(node) -> ASTNode:
    metadata = _extract_metadata(node)
    ast_node = ASTNode(
        node_type=type(node).__name__,
        name=getattr(node, "name", None),
        language="java",
        metadata=metadata,
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


def _extract_metadata(node):
    if not isinstance(node, javalang.tree.Node):
        return None

    metadata = {}

    annotations = getattr(node, "annotations", None)
    if annotations:
        serialized = []
        for annotation in annotations:
            serialized_annotation = _serialize_annotation(annotation)
            if serialized_annotation:
                serialized.append(serialized_annotation)
        if serialized:
            metadata["annotations"] = serialized

    return metadata or None


def _serialize_annotation(annotation):
    name = getattr(annotation, "name", None)
    if not isinstance(name, str):
        return None

    payload = {"name": name}

    element = getattr(annotation, "element", None)
    if element is None:
        return payload

    args = []
    keywords = {}

    elements = element if isinstance(element, (list, tuple)) else [element]

    for entry in elements:
        if isinstance(entry, javalang.tree.ElementValuePair):
            value = _literal_value(entry.value)
            if entry.name == "value":
                if isinstance(value, list):
                    args.extend(value)
                elif value is not None:
                    args.append(value)
            else:
                keywords[entry.name] = value
        else:
            value = _literal_value(entry)
            if value is not None:
                args.append(value)

    if args:
        payload["args"] = args
    if keywords:
        payload["keywords"] = keywords

    return payload


def _literal_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value

    if isinstance(value, javalang.tree.Literal):
        literal = value.value
        if literal is None:
            return None
        if (literal.startswith("\"") and literal.endswith("\"")) or (
            literal.startswith("'") and literal.endswith("'")
        ):
            return literal[1:-1]
        if literal.lower() in {"true", "false"}:
            return literal.lower() == "true"
        return literal

    if isinstance(value, javalang.tree.MemberReference):
        qualifier = value.qualifier or ""
        member = value.member or ""
        if qualifier.lower() == "requestmethod" and member:
            return member.upper()
        if qualifier and member:
            return f"{qualifier}.{member}"
        return qualifier or member or None

    if isinstance(value, javalang.tree.ElementArrayValue):
        return [
            item for item in (_literal_value(element) for element in value.values)
            if item is not None
        ]

    if isinstance(value, javalang.tree.Annotation):
        return _serialize_annotation(value)

    if isinstance(value, (list, tuple)):
        return [item for item in (_literal_value(element) for element in value) if item is not None]

    return None
