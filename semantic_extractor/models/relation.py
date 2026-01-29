from dataclasses import dataclass


@dataclass
class Relation:
	source: str
	target: str
	relation_type: str      # CALLS, IMPORTS, DEFINES, EXTENDS
	language: str
	file_path: str
