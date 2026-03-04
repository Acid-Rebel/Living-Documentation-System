from __future__ import annotations

from collections.abc import Iterable
from typing import Dict, List, Optional

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.base_detector import BaseApiDetector
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class SpringApiDetector(BaseApiDetector):
    _CLASS_ANNOTATIONS = {"RestController", "Controller"}
    _MAPPING_ANNOTATIONS = {
        "GetMapping": "GET",
        "PostMapping": "POST",
        "PutMapping": "PUT",
        "DeleteMapping": "DELETE",
        "PatchMapping": "PATCH",
        "RequestMapping": None,
    }

    def detect(self, ast_root: ASTNode, file_path: str) -> List[ApiEndpoint]:
        endpoints: List[ApiEndpoint] = []
        self._walk(ast_root, file_path, None, None, endpoints)
        return endpoints

    def _walk(
        self,
        node: ASTNode,
        file_path: str,
        current_class: Optional[str],
        class_path: Optional[str],
        acc: List[ApiEndpoint],
    ) -> None:
        next_class = current_class
        next_class_path = class_path

        if node.node_type == "ClassDeclaration" and node.name:
            annotations = self._collect_annotations(node)
            if self._has_controller_annotation(annotations):
                next_class = node.name
                next_class_path = self._extract_class_level_path(annotations)

        if node.node_type == "MethodDeclaration" and node.name and current_class:
            acc.extend(
                self._extract_method_endpoints(
                    node,
                    file_path,
                    handler_class=current_class,
                    class_path=class_path,
                )
            )

        for child in node.children:
            self._walk(child, file_path, next_class, next_class_path, acc)

    def _extract_method_endpoints(
        self,
        node: ASTNode,
        file_path: str,
        handler_class: str,
        class_path: Optional[str],
    ) -> List[ApiEndpoint]:
        annotations = self._collect_annotations(node)
        endpoints: List[ApiEndpoint] = []

        for annotation in annotations:
            name = annotation.get("name") if isinstance(annotation, dict) else None
            if not isinstance(name, str) or name not in self._MAPPING_ANNOTATIONS:
                continue

            http_method = self._MAPPING_ANNOTATIONS[name]
            if http_method is None:
                http_method = self._resolve_request_mapping_method(annotation)

            paths = self._extract_paths(annotation)
            if class_path:
                paths = [self._join_paths(class_path, path) for path in paths]

            for path in paths:
                endpoints.append(
                    ApiEndpoint(
                        path=path,
                        http_method=http_method or "GET",
                        handler_name=node.name,
                        class_name=handler_class,
                        language="java",
                        file_path=file_path,
                        framework="spring",
                        metadata={"annotation": annotation},
                    )
                )

        return endpoints

    def _collect_annotations(self, node: ASTNode) -> Iterable[Dict]:
        if not node.metadata:
            return []
        annotations = node.metadata.get("annotations")
        if isinstance(annotations, dict):
            return annotations.values()
        if isinstance(annotations, Iterable):
            return annotations
        return []

    def _has_controller_annotation(self, annotations: Iterable[Dict]) -> bool:
        for annotation in annotations:
            name = annotation.get("name") if isinstance(annotation, dict) else None
            if isinstance(name, str) and name.split(".")[-1] in self._CLASS_ANNOTATIONS:
                return True
        return False

    def _extract_class_level_path(self, annotations: Iterable[Dict]) -> Optional[str]:
        for annotation in annotations:
            if not isinstance(annotation, dict):
                continue
            name = annotation.get("name")
            if not isinstance(name, str):
                continue
            if name.split(".")[-1] not in {"RequestMapping", "GetMapping", "PostMapping", "PutMapping", "DeleteMapping", "PatchMapping"}:
                continue
            paths = self._extract_paths(annotation)
            if paths:
                return paths[0]
        return None

    def _extract_paths(self, annotation: Dict) -> List[str]:
        paths: List[str] = []
        if not isinstance(annotation, dict):
            return paths
        args = annotation.get("args")
        if isinstance(args, Iterable):
            for arg in args:
                literal = self._extract_literal(arg)
                if literal:
                    paths.append(literal)
        keywords = annotation.get("keywords")
        if isinstance(keywords, dict):
            for key in ("value", "path"):
                value = keywords.get(key)
                literal = self._extract_literal(value)
                if literal:
                    if isinstance(literal, list):
                        paths.extend(literal)
                    else:
                        paths.append(literal)
        return paths or ["/"]

    def _extract_literal(self, value) -> Optional[str | List[str]]:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            literals: List[str] = []
            for item in value:
                literal = self._extract_literal(item)
                if isinstance(literal, str):
                    literals.append(literal)
            return literals
        if isinstance(value, dict):
            literal = value.get("value")
            if isinstance(literal, str):
                return literal
            if isinstance(literal, list):
                return [item for item in literal if isinstance(item, str)]
        return None

    def _resolve_request_mapping_method(self, annotation: Dict) -> Optional[str]:
        keywords = annotation.get("keywords") if isinstance(annotation, dict) else None
        if not isinstance(keywords, dict):
            return None
        method_value = keywords.get("method")
        if isinstance(method_value, str):
            return method_value.upper()
        if isinstance(method_value, list):
            for item in method_value:
                literal = self._extract_literal(item)
                if isinstance(literal, str):
                    return literal.upper()
        return None

    def _join_paths(self, parent: str, child: str) -> str:
        parent = parent.rstrip("/") or "/"
        child = child.lstrip("/")
        if parent == "/":
            return f"/{child}" if child else parent
        return f"{parent}/{child}" if child else parent
