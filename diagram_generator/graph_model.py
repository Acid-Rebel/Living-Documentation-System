from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class ClassInfo:
    methods: Set[str] = field(default_factory=set)
    attributes: Set[str] = field(default_factory=set)
    bases: Set[str] = field(default_factory=set)
    module: str = None
    is_abstract: bool = False

@dataclass
class DiagramGraph:
    classes: Dict[str, ClassInfo] = field(default_factory=dict)
    inheritance: Set[tuple] = field(default_factory=set)
    composition: Set[tuple] = field(default_factory=set)
    usage: Set[tuple] = field(default_factory=set)
    dependencies: Set[tuple] = field(default_factory=set)

