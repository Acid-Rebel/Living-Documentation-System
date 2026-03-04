from __future__ import annotations

from collections.abc import Iterable
from typing import Dict, List, Optional

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.base_detector import BaseApiDetector
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class DjangoApiDetector(BaseApiDetector):
    _SUPPORTED_CALLS = {"path", "re_path", "url"}

    def detect(self, ast_root: ASTNode, file_path: str) -> List[ApiEndpoint]:
        call_nodes = self._collect_urlpattern_calls(ast_root)
        endpoints: List[ApiEndpoint] = []
        for call in call_nodes:
            endpoint = self._call_to_endpoint(call, file_path)
            if endpoint:
                endpoints.append(endpoint)
        return endpoints

    def _collect_urlpattern_calls(self, root: ASTNode) -> List[ASTNode]:
        calls: List[ASTNode] = []

        def visit(node: ASTNode) -> None:
            calls.extend(self._calls_from_assignment(node))
            for child in node.children:
                visit(child)

        visit(root)
        return calls

    def _calls_from_assignment(self, node: ASTNode) -> List[ASTNode]:
        if node.node_type not in {"Assign", "AnnAssign", "AugAssign"}:
            return []
        if not self._targets_urlpatterns(node):
            return []

        sequence_nodes: List[ASTNode] = []
        for child in node.children:
            if child.node_type == "List" or child.node_type == "Tuple":
                sequence_nodes.append(child)

        if node.node_type == "Assign" and not sequence_nodes:
            # handle direct assignment like urlpatterns = path(...)
            sequence_nodes = [child for child in node.children if child.node_type == "Call"]

        calls: List[ASTNode] = []
        for seq in sequence_nodes:
            calls.extend(self._extract_calls(seq))
        return calls

    def _targets_urlpatterns(self, node: ASTNode) -> bool:
        for child in node.children:
            if child.node_type != "Name":
                continue
            metadata = child.metadata or {}
            if metadata.get("id") == "urlpatterns" and metadata.get("ctx") in {"Store", "AugStore", "Load"}:
                return True
        return False

    def _extract_calls(self, seq_node: ASTNode) -> List[ASTNode]:
        calls: List[ASTNode] = []
        for child in seq_node.children:
            if child.node_type == "Call":
                calls.append(child)
            elif child.node_type in {"List", "Tuple"}:
                calls.extend(self._extract_calls(child))
        return calls

    def _call_to_endpoint(self, call_node: ASTNode, file_path: str) -> Optional[ApiEndpoint]:
        metadata = call_node.metadata or {}
        func_name = metadata.get("func")
        if not func_name:
            return None

        func_basename = func_name.split(".")[-1]
        if func_basename not in self._SUPPORTED_CALLS:
            return None

        arg_nodes, keyword_nodes = self._split_call_arguments(call_node)
        if not arg_nodes:
            return None

        path_value = self._literal_value(arg_nodes[0])
        if not isinstance(path_value, str):
            return None
        if not path_value.startswith("/") and not path_value.startswith("^"):
            path_value = "/" + path_value

        view_node = arg_nodes[1] if len(arg_nodes) > 1 else None
        handler_name = self._extract_handler_name(view_node)
        class_name = self._extract_class_name(handler_name)

        keyword_values = self._extract_keywords(keyword_nodes)
        route_name = keyword_values.get("name")

        metadata_payload: Dict[str, object] = {
            "resolver": func_name,
            "route_name": route_name,
        }
        if handler_name:
            metadata_payload["view"] = handler_name

        http_method = "ANY"

        return ApiEndpoint(
            path=path_value,
            http_method=http_method,
            handler_name=handler_name or "<anonymous>",
            class_name=class_name,
            language="python",
            file_path=file_path,
            framework="django",
            metadata=metadata_payload,
        )

    def _split_call_arguments(self, call_node: ASTNode) -> tuple[List[ASTNode], List[ASTNode]]:
        args: List[ASTNode] = []
        keywords: List[ASTNode] = []
        encountered_callable = False
        for child in call_node.children:
            if not encountered_callable and child.node_type in {"Name", "Attribute"}:
                encountered_callable = True
                continue
            if child.node_type == "keyword":
                keywords.append(child)
                continue
            if child.node_type == "Load":
                continue
            args.append(child)
        return args, keywords

    def _extract_keywords(self, keyword_nodes: Iterable[ASTNode]) -> Dict[str, object]:
        values: Dict[str, object] = {}
        for node in keyword_nodes:
            metadata = node.metadata or {}
            arg_name = metadata.get("arg")
            if not arg_name:
                continue
            value_node = next((child for child in node.children if child.node_type != "Load"), None)
            value = self._literal_value(value_node)
            if value is not None:
                values[arg_name] = value
        return values

    def _literal_value(self, node: Optional[ASTNode]):
        if node is None:
            return None
        metadata = node.metadata or {}
        if "value" in metadata:
            return metadata["value"]
        if node.node_type == "List" or node.node_type == "Tuple":
            values = [self._literal_value(child) for child in node.children if child.node_type != "Load"]
            return [value for value in values if value is not None]
        if node.node_type == "Name":
            return metadata.get("id") or node.name
        if node.node_type == "Attribute":
            if "value" in metadata:
                return metadata["value"]
            value_part = next((child for child in node.children if child.node_type != "Load"), None)
            literal = self._literal_value(value_part)
            if literal:
                return f"{literal}.{node.name}" if node.name else literal
        if node.node_type == "Call":
            return metadata.get("func")
        return None

    def _extract_handler_name(self, node: Optional[ASTNode]) -> Optional[str]:
        literal = self._literal_value(node)
        if isinstance(literal, str):
            return literal
        return None

    def _extract_class_name(self, handler_name: Optional[str]) -> Optional[str]:
        if not handler_name:
            return None
        if handler_name.endswith(".as_view"):
            return handler_name.rsplit(".", 1)[0]
        return None