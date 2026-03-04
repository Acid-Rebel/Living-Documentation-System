from dataclasses import dataclass
from typing import Optional

@dataclass
class Symbol:
    name: str
    symbol_type: str       # function, class, method, variable
    language: str
    file_path: str
    parent: Optional[str] = None