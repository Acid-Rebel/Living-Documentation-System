from typing import List, Optional, Sequence, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.symbol import Symbol

_ContextEntry = Tuple[Optional[str], str]


class JavaSymbolAnalyzer(BaseAnalyzer):
    _CLASS_NODES = {
        "ClassDeclaration",
        "InterfaceDeclaration",
        "EnumDeclaration",
        "AnnotationDeclaration",
    }
    _METHOD_NODES = {"MethodDeclaration", "ConstructorDeclaration"}
    _SCOPE_PUSH_NODES = _CLASS_NODES

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Symbol]:
        symbols: List[Symbol] = []
        self._walk(ast_root, file_path, (), None, symbols)
        return symbols

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        package: Optional[str],
        acc: List[Symbol],
    ) -> Optional[str]:
        current_package = package
        next_context = context

        if node.node_type == "PackageDeclaration":
            extracted = self._extract_identifier(node)
            if extracted:
                current_package = extracted

        if node.node_type in self._CLASS_NODES and node.name:
            qualified_name = self._qualify(current_package, context, node.name)
            parent_name = self._qualify(current_package, context) or current_package
            acc.append(
                Symbol(
                    name=qualified_name,
                    symbol_type="class",
                    language="java",
                    file_path=file_path,
                    parent=parent_name,
                )
            )
            next_context = (*context, (node.name, node.node_type))
        elif node.node_type in self._METHOD_NODES and node.name:
            qualified_name = self._qualify(current_package, context, node.name)
            parent_name = self._qualify(current_package, context)
            acc.append(
                Symbol(
                    name=qualified_name,
                    symbol_type="method",
                    language="java",
                    file_path=file_path,
                    parent=parent_name,
                )
            )

        for child in node.children:
            child_package = self._walk(child, file_path, next_context, current_package, acc)
            if child_package and child_package != current_package:
                current_package = child_package

        return current_package

    def _qualify(
        self,
        package: Optional[str],
        context: Sequence[_ContextEntry],
        name: Optional[str] = None,
    ) -> str:
        parts = []
        if package:
            parts.append(package)
        parts.extend(entry[0] for entry in context if entry[0])
        if name:
            parts.append(name)
        return ".".join(parts)

    def _extract_identifier(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            for key in ("name", "identifier", "value", "qualifier"):
                value = node.metadata.get(key)
                if isinstance(value, str) and value:
                    return value
        if node.children:
            parts: List[str] = []
            for child in node.children:
                child_value = self._extract_identifier(child)
                if child_value:
                    parts.append(child_value)
            if parts:
                return ".".join(parts)
        return None
