CLASS_NODES = {"ClassDef"}
METHOD_NODES = {"FunctionDef"}
CALL_NODES = {"Call"}
ASSIGN_NODES = {"Assign", "AnnAssign"}


def extract_ast_relations(ast_root, module=None):
    classes = {}
    relations = []

    def walk(node, current_class=None, current_method=None, method_args=None):
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
                relations.append((node.name, str(base), "INHERITS", None))

            current_class = node.name
            current_method = None
            method_args = set()

        # ---------- METHOD ----------
        if node.node_type in METHOD_NODES and current_class and node.name:
            classes[current_class]["methods"].add(node.name)
            current_method = node.name
            method_args = set()
            
            # Extract args if __init__
            if node.name == "__init__":
                # AST structure for arguments needs better parsing in future,
                # but for normalized AST we might need to look at children 'arguments' -> 'arg'
                # Simple recursive finding of 'arg' nodes in the method subtree (shallow)
                for child in node.children:
                     if child.node_type == "arguments":
                         for arg in child.children:
                             if arg.node_type == "arg" and arg.name and arg.name != "self":
                                 method_args.add(arg.name)

        # ---------- ASSIGNMENT (Composition / Aggregation) ----------
        if node.node_type in ASSIGN_NODES and current_class and current_method == "__init__":
            target_name = None
            value_node = None
            annotation_node = None
            
            # Debug

            target_attr = None
            assigned_val = None
            multiplicity = None
            target_type = None
            
            # Analyze children to find components
            for child in node.children:
                # Target: Attribute representing 'self.attr'
                if child.node_type == "Attribute":
                     # Check if it belongs to 'self'
                    is_self = False
                    for grand in child.children:
                        if grand.node_type == "Name":
                             pass
                        
                        name_val = getattr(grand, "name", None)
                        if not name_val and grand.metadata:
                             name_val = grand.metadata.get("id")
                        
                        if grand.node_type == "Name" and name_val == "self":
                            is_self = True
                    
                    if is_self:
                        target_attr = getattr(child, "name", None) 
                        if not target_attr and child.metadata:
                            target_attr = child.metadata.get("attr")

                # Value: Call, Name, List
                elif child.node_type == "Call":
                     assigned_val = child
                elif child.node_type == "Name":
                     assigned_val = child
                
                # Annotation: Subscript, Name
                elif child.node_type == "Subscript":
                     # Check for List[...]
                     
                     container_type = None
                     inner_type = None
                     
                     for sub in child.children:
                         if sub.node_type == "Name":
                             sub_name = getattr(sub, "name", None)
                             if not sub_name and sub.metadata:
                                 sub_name = sub.metadata.get("id")

                             if not container_type:
                                 container_type = sub_name
                             else:
                                 inner_type = sub_name
                    
                     if container_type in ("List", "Set", "Iterable", "Sequence"):
                         multiplicity = "0..*"
                         target_type = inner_type
                
                elif child.node_type == "Name" and not assigned_val and not target_attr:
                     pass

            # Logic for Relationship
            if target_attr:
                classes[current_class]["attributes"].add(target_attr)
                
                # Case 1: Type Hint defines relation (Aggregation mostly, or Composite if initialized)
                if target_type:
                     relations.append((current_class, target_type, "AGGREGATION", multiplicity))
                
                # Case 2: Value defines relation
                elif assigned_val:
                    if assigned_val.node_type == "Call":
                        # Composition: self.engine = Engine()
                        target = getattr(assigned_val, "call_target", None)
                        if target:
                            relations.append((current_class, target, "COMPOSITION", "1"))

        # ---------- CALL (AST-BASED) ----------
        if node.node_type in CALL_NODES and current_class:
            # FIX: Use normalized call_target if available
            target = getattr(node, "call_target", None)
            if target:
                # We only care about calls to OTHER things
                relations.append((current_class, target, "CALLS", None))

        # ---------- RECURSE ----------
        for child in node.children:
            walk(child, current_class, current_method, method_args)

    walk(ast_root)
    return classes, relations
