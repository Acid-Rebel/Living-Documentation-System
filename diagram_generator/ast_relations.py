CLASS_NODES = {"ClassDef"}
METHOD_NODES = {"FunctionDef"}
CALL_NODES = {"Call"}


def extract_ast_relations(ast_root, module=None):
    classes = {}
    relations = []

    def walk(node, current_class=None):
        # ---------- CLASS ----------
        if node.node_type in CLASS_NODES and node.name:
            classes.setdefault(
                node.name,
                {
                    "methods": set(),
                    "attributes": set(),
                    "module": module,
                },
            )

            # Inheritance
            for base in getattr(node, "bases", []) or []:
                relations.append((node.name, str(base), "INHERITS"))

            current_class = node.name

        # ---------- METHOD ----------
        if node.node_type in METHOD_NODES and current_class and node.name:
            classes[current_class]["methods"].add(node.name)

        # ---------- CALL (CLASS-LEVEL HEURISTIC) ----------
        if node.node_type in CALL_NODES and current_class:
            # Collapse method calls → class call
            relations.append((current_class, current_class, "CALLS"))

        # ---------- RECURSE ----------
        for child in node.children:
            walk(child, current_class)

    walk(ast_root)
    return classes, relations
