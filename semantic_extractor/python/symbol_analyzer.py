from typing import List, Optional, Sequence, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.symbol import Symbol


_ContextEntry = Tuple[Optional[str], str]


class PythonSymbolAnalyzer(BaseAnalyzer):
    _CLASS_NODES = {"ClassDef"}
    _FUNCTION_NODES = {"FunctionDef", "AsyncFunctionDef"}

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Symbol]:
        symbols: List[Symbol] = []
        self._walk(ast_root, file_path, (), symbols)
        return symbols

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        acc: List[Symbol],
    ) -> None:
        next_context = context
        if node.node_type in self._CLASS_NODES:
            qualified_name = self._qualify(context, node.name)
            acc.append(
                Symbol(
                    name=qualified_name,
                    symbol_type="class",
                    language="python",
                    file_path=file_path,
                    parent=self._qualify(context) or None,
                )
            )
            if node.name:
                next_context = (*context, (node.name, node.node_type))
        elif node.node_type in self._FUNCTION_NODES:
            qualified_name = self._qualify(context, node.name)
            symbol_type = "method" if self._has_class_parent(context) else "function"
            acc.append(
                Symbol(
                    name=qualified_name,
                    symbol_type=symbol_type,
                    language="python",
                    file_path=file_path,
                    parent=self._qualify(context) or None,
                )
            )
            if node.name:
                next_context = (*context, (node.name, node.node_type))

        for child in node.children:
            self._walk(child, file_path, next_context, acc)

    def _qualify(
        self,
        context: Sequence[_ContextEntry],
        name: Optional[str] = None,
    ) -> str:
        parts = [entry[0] for entry in context if entry[0]]
        if name:
            parts.append(name)
        return ".".join(parts)

    def _has_class_parent(self, context: Sequence[_ContextEntry]) -> bool:
        return any(entry[1] in self._CLASS_NODES for entry in reversed(context))
