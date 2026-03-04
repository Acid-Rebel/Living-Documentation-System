from __future__ import annotations

from typing import Dict, List

from code_parser.ast_schema import ASTNode

from api_endpoint_detector.base_detector import BaseApiDetector
from api_endpoint_detector.models.api_endpoint import ApiEndpoint
from api_endpoint_detector.python.django_detector import DjangoApiDetector
from api_endpoint_detector.python.fastapi_detector import FastApiDetector
from api_endpoint_detector.python.flask_detector import FlaskApiDetector
from api_endpoint_detector.java.spring_detector import SpringApiDetector


class DetectorManager:
    def __init__(self) -> None:
        self._detectors: Dict[str, List[BaseApiDetector]] = {
            "python": [FlaskApiDetector(), FastApiDetector(), DjangoApiDetector()],
            "java": [SpringApiDetector()],
        }

    def detect(self, ast_root: ASTNode, file_path: str, language: str) -> List[ApiEndpoint]:
        language_key = language.lower()
        detectors = self._detectors.get(language_key, [])
        if not detectors:
            return []

        endpoints: List[ApiEndpoint] = []
        for detector in detectors:
            endpoints.extend(detector.detect(ast_root, file_path))
        return endpoints
