from typing import List, Optional, Sequence, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.relation import Relation

_ContextEntry = Tuple[Optional[str], str]


class JavaCallAnalyzer(BaseAnalyzer):
    _CLASS_NODES = {
        "ClassDeclaration",
        "InterfaceDeclaration",
        "EnumDeclaration",
        "AnnotationDeclaration",
    }
    _CALLABLE_NODES = {"MethodDeclaration", "ConstructorDeclaration"}
    _CALL_NODES = {"MethodInvocation", "SuperMethodInvocation", "ExplicitConstructorInvocation"}

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Relation]:
        relations: List[Relation] = []
        self._walk(ast_root, file_path, (), None, None, relations)
        return relations

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        package: Optional[str],
        current_callable: Optional[str],
        acc: List[Relation],
    ) -> None:
        current_package = package
        next_context = context
        next_callable = current_callable

        if node.node_type == "PackageDeclaration":
            package_name = self._extract_identifier(node)
            if package_name:
                current_package = package_name

        if node.node_type in self._CLASS_NODES and node.name:
            next_context = (*context, (node.name, node.node_type))

        if node.node_type in self._CALLABLE_NODES and node.name:
            next_callable = self._qualify(current_package, context, node.name)

        if node.node_type in self._CALL_NODES:
            caller = next_callable or self._qualify(current_package, context) or file_path
            callee = self._extract_identifier(node)
            if callee and caller:
                acc.append(
                    Relation(
                        source=caller,
                        target=callee,
                        relation_type="CALLS",
                        language="java",
                        file_path=file_path,
                    )
                )

        for child in node.children:
            self._walk(child, file_path, next_context, current_package, next_callable, acc)

    def _qualify(
        self,
        package: Optional[str],
        context: Sequence[_ContextEntry],
        name: Optional[str] = None,
    ) -> Optional[str]:
        parts: List[str] = []
        if package:
            parts.append(package)
        parts.extend(entry[0] for entry in context if entry[0])
        if name:
            parts.append(name)
        return ".".join(parts) if parts else name

    def _extract_identifier(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            for key in (
                "member",
                "name",
                "identifier",
                "value",
                "type",
                "qualifier",
            ):
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
