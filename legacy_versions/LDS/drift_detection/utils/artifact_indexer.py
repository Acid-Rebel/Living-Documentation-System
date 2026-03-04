from dataclasses import asdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

from api_endpoint_detector.models.api_endpoint import ApiEndpoint
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol

_HandlerIdentity = Tuple[str, str, str, str]
_SymbolIdentity = Tuple[str, str]
_DependencyIdentity = Tuple[str, str, str, str]


def handler_identity(endpoint: ApiEndpoint) -> _HandlerIdentity:
    class_name = endpoint.class_name or ""
    return (
        endpoint.language or "",
        endpoint.framework or "",
        class_name,
        endpoint.handler_name,
    )


def build_handler_map(endpoints: Iterable[ApiEndpoint]) -> Dict[_HandlerIdentity, ApiEndpoint]:
    mapping: Dict[_HandlerIdentity, ApiEndpoint] = {}
    for endpoint in endpoints:
        mapping[handler_identity(endpoint)] = endpoint
    return mapping


def build_endpoint_signature(endpoint: ApiEndpoint) -> Tuple[str, str, str]:
    return (
        endpoint.language or "",
        endpoint.http_method.upper(),
        endpoint.path,
    )


def build_symbol_name_set(symbols: Iterable[Symbol]) -> Set[_SymbolIdentity]:
    return {
        (symbol.language or "", symbol.name)
        for symbol in symbols
    }


def candidate_handler_names(endpoint: ApiEndpoint) -> List[str]:
    names = [endpoint.handler_name]
    if endpoint.class_name:
        names.append(f"{endpoint.class_name}.{endpoint.handler_name}")
        names.append(endpoint.class_name)
    return names


def is_dependency_relation(relation: Relation) -> bool:
    relation_type = relation.relation_type.upper()
    return "IMPORT" in relation_type or "DEPEND" in relation_type


def build_dependency_set(relations: Iterable[Relation]) -> Set[_DependencyIdentity]:
    dependencies: Set[_DependencyIdentity] = set()
    for relation in relations:
        if not is_dependency_relation(relation):
            continue
        dependencies.add(
            (
                relation.language or "",
                relation.relation_type,
                relation.source,
                relation.target,
            )
        )
    return dependencies


def index_dependencies(relations: Iterable[Relation]) -> Dict[_DependencyIdentity, Relation]:
    mapping: Dict[_DependencyIdentity, Relation] = {}
    for relation in relations:
        if not is_dependency_relation(relation):
            continue
        key = (
            relation.language or "",
            relation.relation_type,
            relation.source,
            relation.target,
        )
        mapping[key] = relation
    return mapping


def is_symbol_reference_relation(relation: Relation) -> bool:
    tokens = ("CALL", "REFERENCE", "REFERS", "USE", "USES", "INVOKE")
    relation_type = relation.relation_type.upper()
    return any(token in relation_type for token in tokens)


def relation_to_metadata(relation: Relation) -> Dict:
    return asdict(relation)


def endpoint_to_metadata(endpoint: ApiEndpoint) -> Dict:
    return asdict(endpoint)
