from typing import Dict, Set


class ClassInfo:
    """
    Holds structural information for a class.
    """

    def __init__(self, module: str = None):
        self.module = module
        self.methods: Set[str] = set()
        self.attributes: Set[str] = set()
        self.is_abstract: bool = False



class DiagramGraph:
    """
    Unified graph model built from semantic analysis + AST heuristics.
    """

    def __init__(self):
        self.classes: Dict[str, ClassInfo] = {}

        # Relationships
        self.inheritance: Set[tuple[str, str]] = set()    # (child, parent)
        self.dependencies: Set[tuple[str, str]] = set()  # (module, module)
        self.usage: Set[tuple[str, str]] = set()          # (class, class)
        self.composition: Set[tuple[str, str]] = set()    # (class, class)
        self.calls: Set[tuple[str, str]] = set()          # (class, class) ✅ FIX
        self.calls_heuristic: Set[tuple[str, str]] = set()


    def load_from_semantics(self, symbols, relations):
        """
        Populate the graph using semantic symbols and relations.

        Expected schemas:
        - Symbol: name, symbol_type, file_path, parent
        - Relation: source, target, relation_type
        """

        # ---------- Load symbols ----------
        for sym in symbols:
            stype = sym.symbol_type

            # ---- Class ----
            if stype == "class":
                if sym.name not in self.classes:
                    self.classes[sym.name] = ClassInfo(
                        module=sym.file_path
                    )

            # ---- Method ----
            elif stype == "method" and sym.parent:
                if sym.parent in self.classes:
                    self.classes[sym.parent].methods.add(sym.name)

            # ---- Attribute ----
            elif stype == "attribute" and sym.parent:
                if sym.parent in self.classes:
                    self.classes[sym.parent].attributes.add(sym.name)

        # ---------- Load relations ----------
        for rel in relations:
            src = rel.source
            tgt = rel.target
            rtype = rel.relation_type.lower()

            if src == tgt:
                continue

            # ---- Inheritance ----
            if rtype == "inheritance":
                self.inheritance.add((src, tgt))

            # ---- Composition ----
            elif rtype == "composition":
                self.composition.add((src, tgt))

            # ---- Call ----
            elif rtype == "CALLS":
                if src != dst:
                    self.calls_heuristic.add((src, dst))


            # ---- Usage ----
            elif rtype == "usage":
                self.usage.add((src, tgt))

            # ---- Dependency (imports) ----
            elif rtype == "import":
                self.dependencies.add((src, tgt))

    def add_ast_relations(self, classes, relations):
        # ---------- Classes ----------
        for cls, info in classes.items():
            if cls not in self.classes:
                self.classes[cls] = ClassInfo(module=info["module"])
    
            self.classes[cls].methods.update(info["methods"])
            self.classes[cls].attributes.update(info["attributes"])
    
        # ---------- Relations ----------
        for src, dst, rtype in relations:
            if rtype == "INHERITS":
                if src != dst:
                    self.inheritance.add((src, dst))
    
            elif rtype == "CALLS":
                # FIX 1: AST calls are weak → usage only
                if src != dst:
                    self.usage.add((src, dst))
