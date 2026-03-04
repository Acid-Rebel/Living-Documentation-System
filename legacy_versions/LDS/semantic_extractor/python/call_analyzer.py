from typing import List, Optional, Sequence, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.relation import Relation

_ContextEntry = Tuple[Optional[str], str]


class PythonCallAnalyzer(BaseAnalyzer):
    _SCOPE_NODES = {"ClassDef", "FunctionDef", "AsyncFunctionDef"}
    _CALL_NODES = {"Call"}

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Relation]:
        relations: List[Relation] = []
        self._walk(ast_root, file_path, (), None, relations)
        return relations

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        current_callable: Optional[str],
        acc: List[Relation],
    ) -> None:
        next_context = context
        next_callable = current_callable

        if node.node_type in self._SCOPE_NODES:
            appended = (node.name if node.name else None, node.node_type)
            next_context = (*context, appended)
            if node.node_type in {"FunctionDef", "AsyncFunctionDef"} and node.name:
                next_callable = self._qualify(context, node.name)

        if node.node_type in self._CALL_NODES:
            caller = next_callable or self._module_identifier(file_path)
            callee = self._extract_call_target(node)
            if callee:
                acc.append(
                    Relation(
                        source=caller,
                        target=callee,
                        relation_type="CALLS",
                        language="python",
                        file_path=file_path,
                    )
                )

        for child in node.children:
            self._walk(child, file_path, next_context, next_callable, acc)

    def _qualify(
        self,
        context: Sequence[_ContextEntry],
        name: Optional[str],
    ) -> str:
        parts = [entry[0] for entry in context if entry[0]]
        if name:
            parts.append(name)
        return ".".join(parts)

    def _module_identifier(self, file_path: str) -> str:
        return file_path

    def _extract_call_target(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            for key in (
                "call_name",
                "qualified_name",
                "name",
                "id",
                "identifier",
                "target",
                "value",
            ):
                value = node.metadata.get(key)
                if isinstance(value, str) and value:
                    return value
        for child in node.children:
            identifier = self._extract_identifier(child)
            if identifier:
                return identifier
        return None

    def _extract_identifier(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            parts = []
            for key in ("name", "id", "identifier", "value", "attr"):
                value = node.metadata.get(key)
                if isinstance(value, str) and value:
                    parts.append(value)
            if parts:
                return ".".join(parts)
        if node.children:
            sub_parts = []
            for child in node.children:
                child_id = self._extract_identifier(child)
                if child_id:
                    sub_parts.append(child_id)
            if sub_parts:
                return ".".join(sub_parts)
        return None
