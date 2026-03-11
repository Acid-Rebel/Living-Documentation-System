# Testing Strategy - Living-Documentation-System

This document outlines the testing strategy and pipeline plan for the project to ensure high code quality, reliability, and maintainability.

## 1. Objectives
- Maximize test coverage for core business logic.
- Ensure API reliability and contract adherence.
- **Environment Agnostic**: Enable full test suites to run in any environment (CI/CD, local, air-gapped) using robust mocking.
- Verify integration between different modules (API, Engine, Parsers).

## 2. Testing Levels

### Unit Testing
- **Scope**: Individual functions and classes in `core/` and `living_docs_engine/`.
- **Tools**: `pytest`.
- **Focus**: Edge cases, logic branches, and error handling.

### Integration Testing
- **Scope**: Interactions between modules, such as `core.api` calling `living_docs_engine.semantic_insights`.
- **Tools**: `pytest`, `httpx` (for API calls).

### API Testing
- **Scope**: FastAPI endpoints in `core/api.py`.
- **Tools**: `FastAPI TestClient`.
- **Focus**: Response status codes, JSON structure, and error messages.

## 3. Mocking and Hardware Independence
To ensure tests are fast and reliable, we use extensive mocking:
- **AI Service Mocks**: Google (Gemini), OpenAI, and AWS (Bedrock) clients are mocked to prevent real API calls and handle missing credentials.
- **File System Mocks**: `unittest.mock.patch` is used for operations involving I/O to prevent side effects.

## 4. Legacy Support and Compatibility
The project maintains compatibility with legacy versions (found in `legacy_versions/`).
- **Conditional Skipping**: Tests requiring dependencies not present in the current environment (e.g., `django`, `markdown`) are automatically skipped using `pytest.skip` rather than failing collection.

## 5. Remaining Gaps & Roadmap
The following areas are currently not covered and are prioritized for future development:
- **End-to-End (E2E) Testing**: Full user workflows from repository ingestion to diagram generation.
- **Performance Testing**: Benchmarking the engine against large-scale repositories (100k+ lines of code).
- **Automated Dependency Management**: Containerized testing environments for legacy suites to avoid manual skipping.
- **Coverage Enforcement**: Implementing `pytest-cov` with a minimum threshold (e.g., 80%) in CI/CD.

## 6. CI/CD Pipeline
- **Platform**: GitHub Actions.
- **Steps**:
  1. Setup Python environment.
  2. Install dependencies.
  3. Run tests with `pytest`.
  4. Generate coverage reports.
