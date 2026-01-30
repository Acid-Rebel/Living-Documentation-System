from diagram_generator.graph_model import ClassInfo

# Unified node types (language-agnostic)
CLASS_NODES = {"ClassDef", "ClassDeclaration"}
METHOD_NODES = {"FunctionDef", "MethodDeclaration"}
ATTRIBUTE_NODES = {"Assign", "FieldDeclaration"}
IMPORT_NODES = {"Import", "ImportFrom", "ImportDeclaration"}
BASE_NODES = {"Base", "Superclass"}


def traverse(node, graph, current_class=None, module=None):
    """
    Traverses the unified AST and extracts:
    - Classes
    - Methods
    - Attributes
    - Inheritance
    - Module dependencies (pyreverse-style)
    - Heuristic composition + usage relationships
    """

    # ---------- CLASS ----------
    if node.node_type in CLASS_NODES and node.name:
        if node.name not in graph.classes:
            graph.classes[node.name] = ClassInfo(module=module)
        current_class = node.name

        # ✅ FIX: extract inheritance from class bases (pyreverse-style)
        bases = getattr(node, "bases", None)
        if bases:
            for base in bases:
                base_name = str(base)
                graph.inheritance.add((base_name, current_class))

    
    # Detect abstract class (Python-safe)
    if node.node_type in CLASS_NODES:
        decorators = getattr(node, "decorators", None)
        if decorators:
            for deco in decorators:
                if "abstract" in str(deco).lower():
                    graph.classes[node.name].is_abstract = True


    # # ---------- INHERITANCE ----------
    # if node.node_type in BASE_NODES and current_class and node.name:
    #     graph.inheritance.add((node.name, current_class))

    # ---------- METHOD ----------
    if node.node_type in METHOD_NODES and current_class and node.name:
        graph.classes[current_class].methods.add(node.name)

    # ---------- ATTRIBUTE ----------
    if node.node_type in ATTRIBUTE_NODES and current_class and node.name:
        graph.classes[current_class].attributes.add(node.name)

    # ---------- MODULE DEPENDENCY ----------
    if node.node_type in IMPORT_NODES and node.name and module:
        imported_module = node.name.split(".")[0]
        current_module = module.split(".")[0]
    
        if imported_module != current_module:
            graph.dependencies.add((current_module, imported_module))


    # ---------- HEURISTIC RELATIONSHIP GUESSER ----------
    # FIX #2: skip heuristic inference for test classes
    if current_class and not current_class.lower().startswith("test"):
        node_name = (node.name or "").lower()
    
        for cls in graph.classes:
            cls_lower = cls.lower()
    
            # avoid self-loops
            if cls == current_class:
                continue
    
            if cls_lower in node_name:
                graph.usage.add((current_class, cls))
    
            if node.node_type == "Assign" and cls_lower in node_name:
                graph.composition.add((current_class, cls))
    

    # ---------- RECURSE ----------
    for child in node.children:
        traverse(child, graph, current_class, module)
