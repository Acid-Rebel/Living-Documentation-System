from abc import ABC, abstractmethod
from typing import List

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class BaseApiDetector(ABC):
	@abstractmethod
	def detect(self, ast_root: ASTNode, file_path: str) -> List[ApiEndpoint]:
		"""Return API endpoints detected in the given AST."""
		raise NotImplementedError
