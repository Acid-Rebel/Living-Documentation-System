
import pytest
from diagram_generator.heuristics import enrich_with_heuristics
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol

def test_enrich_with_heuristics_import_to_call():
    # Setup: 1 import relation
    rel = Relation(
        source="A", target="B", relation_type="import",
        language="python", file_path="foo.py"
    )
    relations = [rel]
    symbols = [] # Unused currently by logic, but required by sig
    
    enriched = enrich_with_heuristics(symbols, relations)
    
    # Expect 2 relations: original import + new call
    assert len(enriched) == 2
    assert enriched[0].relation_type == "import"
    assert enriched[1].relation_type == "call"
    assert enriched[1].source == "A"
    assert enriched[1].target == "B"

def test_enrich_no_change_for_others():
    rel = Relation(
        source="A", target="B", relation_type="inherits",
        language="python", file_path="foo.py"
    )
    relations = [rel]
    enriched = enrich_with_heuristics([], relations)
    
    assert len(enriched) == 1
    assert enriched[0].relation_type == "inherits"
