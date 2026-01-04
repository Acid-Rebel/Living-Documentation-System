from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

@dataclass
class ASTNode:
    """Represenation of a node in the AST."""
    node_type: str
    name : Optional[str] = None
    language: Optional[str] = None
    children: List["ASTNode"] = field(default_factory=list)
    metadata: Optional[Mapping[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type,
            "name": self.name,
            "language": self.language,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
        }