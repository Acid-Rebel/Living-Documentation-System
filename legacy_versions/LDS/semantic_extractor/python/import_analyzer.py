from collections.abc import Iterable as IterableABC
from typing import Iterable, List, Optional, Sequence, Set, Tuple

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.models.relation import Relation

_ContextEntry = Tuple[Optional[str], str]


class PythonImportAnalyzer(BaseAnalyzer):
    _SCOPE_NODES = {"ClassDef", "FunctionDef", "AsyncFunctionDef"}
    _IMPORT_NODES = {"Import", "ImportFrom"}

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Relation]:
        relations: List[Relation] = []
        self._walk(ast_root, file_path, (), relations)
        return relations

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        context: Sequence[_ContextEntry],
        acc: List[Relation],
    ) -> None:
        next_context = context
        if node.node_type in self._IMPORT_NODES:
            source = self._scope_identifier(context, file_path)
            targets = self._collect_targets(node)
            for target in targets:
                acc.append(
                    Relation(
                        source=source,
                        target=target,
                        relation_type="IMPORTS",
                        language="python",
                        file_path=file_path,
                    )
                )

        if node.node_type in self._SCOPE_NODES and node.name:
            next_context = (*context, (node.name, node.node_type))

        for child in node.children:
            self._walk(child, file_path, next_context, acc)

    def _collect_targets(self, node: ASTNode) -> Iterable[str]:
        targets: Set[str] = set()
        if node.metadata:
            metadata_targets = self._metadata_targets(node.metadata)
            targets.update(metadata_targets)

        for child in node.children:
            identifier = self._node_identifier(child)
            if identifier:
                module_prefix = self._metadata_module(node)
                if module_prefix and identifier != module_prefix:
                    targets.add(f"{module_prefix}.{identifier}")
                else:
                    targets.add(identifier)

        if not targets and node.name:
            targets.add(node.name)

        return sorted(targets)

    def _metadata_targets(self, metadata: dict) -> Iterable[str]:
        for key in ("targets", "modules", "names", "identifiers"):
            raw = metadata.get(key)
            if isinstance(raw, str):
                yield raw
            elif isinstance(raw, IterableABC):
                for item in raw:
                    if isinstance(item, str):
                        yield item

    def _metadata_module(self, node: ASTNode) -> Optional[str]:
        if node.metadata:
            for key in ("module", "package", "namespace"):
                value = node.metadata.get(key)
                if isinstance(value, str) and value:
                    return value
        return None

    def _node_identifier(self, node: ASTNode) -> Optional[str]:
        if node.name:
            return node.name
        if node.metadata:
            for key in ("name", "id", "identifier", "value"):
                value = node.metadata.get(key)
                if isinstance(value, str) and value:
                    return value
        return None

    def _scope_identifier(
        self,
        context: Sequence[_ContextEntry],
        file_path: str,
    ) -> str:
        names = [entry[0] for entry in context if entry[0]]
        if names:
            return ".".join(names)
        return file_path
