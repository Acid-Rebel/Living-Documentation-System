from __future__ import annotations

from collections.abc import Iterable
from typing import Dict, List, Optional, Sequence

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.base_detector import BaseApiDetector
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class FlaskApiDetector(BaseApiDetector):
    _ROUTE_DECORATOR = "route"

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
            acc.extend(
                self._extract_endpoints(node, file_path, class_name=class_name)
            )

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
            if not self._is_route_decorator(decorator):
                continue

            paths = self._extract_paths(decorator)
            methods = self._extract_methods(decorator) or ["GET"]
            for path in paths:
                for method in methods:
                    endpoints.append(
                        ApiEndpoint(
                            path=path,
                            http_method=method.upper(),
                            handler_name=node.name or "<anonymous>",
                            class_name=class_name,
                            language="python",
                            file_path=file_path,
                            framework="flask",
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

    def _is_route_decorator(self, decorator: Dict) -> bool:
        name = self._decorator_name(decorator)
        if not name:
            return False
        return name.endswith(f".{self._ROUTE_DECORATOR}") or name == self._ROUTE_DECORATOR

    def _decorator_name(self, decorator: Dict) -> Optional[str]:
        name = decorator.get("name") if isinstance(decorator, dict) else None
        if isinstance(name, str) and name:
            return name
        return None

    def _extract_paths(self, decorator: Dict) -> List[str]:
        paths: List[str] = []
        args = decorator.get("args") if isinstance(decorator, dict) else None
        if isinstance(args, Iterable):
            for arg in args:
                value = self._extract_literal(arg)
                if value:
                    paths.append(value)
        keywords = decorator.get("keywords") if isinstance(decorator, dict) else None
        if isinstance(keywords, dict):
            for key in ("rule", "path", "url" ):
                value = keywords.get(key)
                if value:
                    literal = self._extract_literal(value)
                    if literal:
                        paths.append(literal)
        return paths or ["/"]

    def _extract_methods(self, decorator: Dict) -> List[str]:
        keywords = decorator.get("keywords") if isinstance(decorator, dict) else None
        if not isinstance(keywords, dict):
            return []
        raw_methods = keywords.get("methods")
        if isinstance(raw_methods, str):
            return [raw_methods]
        if isinstance(raw_methods, Iterable):
            methods: List[str] = []
            for entry in raw_methods:
                literal = self._extract_literal(entry)
                if literal:
                    methods.append(literal)
            return methods
        return []

    def _extract_literal(self, value) -> Optional[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            literal = value.get("value")
            if isinstance(literal, str):
                return literal
        return None
