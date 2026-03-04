from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Dict, List, Optional

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.base_detector import BaseApiDetector
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class FastApiDetector(BaseApiDetector):
    _HTTP_DECORATORS = {
        "get": "GET",
        "post": "POST",
        "put": "PUT",
        "delete": "DELETE",
        "patch": "PATCH",
        "options": "OPTIONS",
        "head": "HEAD",
    }

    def detect(self, ast_root: ASTNode, file_path: str) -> List[ApiEndpoint]:
        endpoints: List[ApiEndpoint] = []
        self._walk(ast_root, file_path, (), endpoints)
        return endpoints

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        class_stack: Sequence[str],
        acc: List[ApiEndpoint],
    ) -> None:
        next_stack = class_stack
        if node.node_type in {"ClassDef", "AsyncClassDef"} and node.name:
            next_stack = (*class_stack, node.name)

        if node.node_type in {"FunctionDef", "AsyncFunctionDef"}:
            class_name = ".".join(next_stack) if next_stack else None
            acc.extend(self._extract_endpoints(node, file_path, class_name))

        for child in node.children:
            self._walk(child, file_path, next_stack, acc)

    def _extract_endpoints(
        self,
        node: ASTNode,
        file_path: str,
        class_name: Optional[str],
    ) -> List[ApiEndpoint]:
        decorators = self._collect_decorators(node)
        endpoints: List[ApiEndpoint] = []
        for decorator in decorators:
            http_method = self._http_method_from_decorator(decorator)
            if not http_method:
                continue

            paths = self._extract_paths(decorator) or ["/"]
            for path in paths:
                endpoints.append(
                    ApiEndpoint(
                        path=path,
                        http_method=http_method,
                        handler_name=node.name or "<anonymous>",
                        class_name=class_name,
                        language="python",
                        file_path=file_path,
                        framework="fastapi",
                        metadata={"decorator": decorator},
                    )
                )
        return endpoints

    def _collect_decorators(self, node: ASTNode) -> Iterable[Dict]:
        if not node.metadata:
            return []
        decorators = node.metadata.get("decorators")
        if isinstance(decorators, dict):
            return decorators.values()
        if isinstance(decorators, Iterable):
            return decorators
        return []

    def _http_method_from_decorator(self, decorator: Dict) -> Optional[str]:
        name = self._decorator_name(decorator)
        if not name:
            return None
        for suffix, method in self._HTTP_DECORATORS.items():
            if name.endswith(f".{suffix}") or name == suffix:
                return method
        return None

    def _decorator_name(self, decorator: Dict) -> Optional[str]:
        if not isinstance(decorator, dict):
            return None
        value = decorator.get("name")
        if isinstance(value, str) and value:
            return value
        return None

    def _extract_paths(self, decorator: Dict) -> List[str]:
        paths: List[str] = []
        if not isinstance(decorator, dict):
            return paths
        args = decorator.get("args")
        if isinstance(args, Sequence):
            for arg in args:
                literal = self._extract_literal(arg)
                if literal:
                    paths.append(literal)
        keywords = decorator.get("keywords")
        if isinstance(keywords, dict):
            for key in ("path", "url", "route", "rule"):
                literal = self._extract_literal(keywords.get(key))
                if literal:
                    paths.append(literal)
        return paths

    def _extract_literal(self, value) -> Optional[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            literal = value.get("value")
            if isinstance(literal, str):
                return literal
        return None
