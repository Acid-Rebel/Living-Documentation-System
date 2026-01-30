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
        self.aggregation: Set[tuple[str, str]] = set()    # (class, class)
        self.calls: Set[tuple[str, str]] = set()          # (class, class) ✅ FIX
        self.calls_heuristic: Set[tuple[str, str]] = set()
        
        # (src, dst) -> label (e.g. "1..*")
        self.multiplicity: Dict[tuple[str, str], str] = {}


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
            # Normalize relation type
            rtype = rel.relation_type.lower()
            if rtype == "calls":
                rtype = "call"
            elif rtype == "imports":
                rtype = "import"

            if src == tgt:
                continue

            # ---- Inheritance ----
            if rtype == "inheritance" or rtype == "inherits":
                self.inheritance.add((src, tgt))

            # ---- Composition ----
            elif rtype == "composition":
                self.composition.add((src, tgt))

            # ---- Aggregation ----
            elif rtype == "aggregation":
                self.aggregation.add((src, tgt))

            # ---- Call (Semantic = Unreliable) ----
            elif rtype == "call":
                 # Semantic calls are unreliable, store as heuristic/usage
                 self.calls_heuristic.add((src, tgt))

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
        for item in relations:
            # Handle 3-tuple or 4-tuple (with multiplicity)
            if len(item) == 4:
                src, dst, rtype, mult = item
                if mult:
                    self.multiplicity[(src, dst)] = mult
            else:
                src, dst, rtype = item

            if src == dst:
                continue

            if rtype == "INHERITS":
                self.inheritance.add((src, dst))
            
            elif rtype == "COMPOSITION":
                self.composition.add((src, dst))
            
            elif rtype == "AGGREGATION":
                self.aggregation.add((src, dst))
    
            elif rtype == "CALLS":
                # AST calls are the reliable source -> graph.calls
                
                # Filter self-calls (method calls within same class)
                # If dst is a method of src, it's a self-call
                if src in self.classes and dst in self.classes[src].methods:
                    continue
                    
                self.calls.add((src, dst))
