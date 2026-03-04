from typing import List, Optional, Sequence, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.relation import Relation

_ContextEntry = Tuple[Optional[str], str]


class JavaImportAnalyzer(BaseAnalyzer):
    _SCOPE_NODES = {
        "ClassDeclaration",
        "InterfaceDeclaration",
        "EnumDeclaration",
        "AnnotationDeclaration",
    }
    _IMPORT_NODES = {"Import", "ImportDeclaration"}

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Relation]:
        relations: List[Relation] = []
        self._walk(ast_root, file_path, (), None, relations)
        return relations

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        package: Optional[str],
        acc: List[Relation],
    ) -> None:
        current_package = package
        next_context = context

        if node.node_type == "PackageDeclaration":
            package_name = self._extract_identifier(node)
            if package_name and package_name != package:
                current_package = package_name
                acc.append(
                    Relation(
                        source=file_path,
                        target=package_name,
                        relation_type="DEFINES",
                        language="java",
                        file_path=file_path,
                    )
                )

        if node.node_type in self._IMPORT_NODES:
            target = self._extract_identifier(node)
            if target:
                acc.append(
                    Relation(
                        source=file_path,
                        target=target,
                        relation_type="IMPORTS",
                        language="java",
                        file_path=file_path,
                    )
                )

        if node.node_type in self._SCOPE_NODES and node.name:
            next_context = (*context, (node.name, node.node_type))

        for child in node.children:
            self._walk(child, file_path, next_context, current_package, acc)

    def _extract_identifier(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            for key in ("name", "path", "identifier", "value", "qualifier"):
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
