from semantic_extractor.models.relation import Relation


def enrich_with_heuristics(symbols, relations):
    """
    Add pyreverse-style heuristics on top of semantic relations.
    """

    enriched = list(relations)

    class_names = {s.name for s in symbols if s.symbol_type == "class"}

    # Import → Call heuristic
    for r in relations:
        if r.relation_type == "import":
            enriched.append(
                Relation(
                    source=r.source,
                    target=r.target,
                    relation_type="call",
                    language=r.language,
                    file_path=r.file_path,
                )
            )

    return enriched
