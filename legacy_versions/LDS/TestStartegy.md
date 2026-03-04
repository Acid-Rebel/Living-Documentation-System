# Test Strategy Document

**Project Name:** Living Documentation System  
**Document Type:** Test Strategy  
**Version:** 1.0  
**Date:** 09/02/2026

---

## 1. Introduction

### 1.1 Purpose

This Test Strategy document defines the overall testing approach, objectives, scope, tools, techniques, and reporting mechanisms used for validating the *Living Documentation System*. It serves as a formal reference for how quality assurance is planned and executed as part of this Software Engineering project.

### 1.2 Project Overview

The Living Documentation System is an automated software analysis and documentation platform that continuously generates and updates architectural documentation directly from source code. It parses codebases, extracts semantics, detects API endpoints, builds dependency graphs, and renders diagrams such as UML class diagrams, call graphs, and dependency diagrams.

The system supports Python and Java codebases and integrates AI-based summarization for README and documentation generation.

---

## 2. Test Objectives

- Verify correctness of code parsing, semantic extraction, and diagram generation  
- Ensure API endpoint detection works accurately across multiple frameworks  
- Validate integration between modules in the analysis pipeline  
- Ensure backend REST APIs behave as expected  
- Confirm immutability and consistency of stored analysis artifacts  
- Prevent regression during feature additions and refactoring  
- Validate system behavior under real-world scenarios using integration tests  

---

## 3. Scope of Testing

### 3.1 In Scope

- Unit testing of all core modules  
- Integration testing of the full analysis pipeline  
- Backend API testing using Django REST Framework  
- API endpoint detection for Django, Flask, FastAPI, and Spring Boot  
- Diagram rendering logic (Mermaid and Graphviz DOT)  
- Dependency analysis and artifact storage  
- AI integration logic with mocked external services  

### 3.2 Out of Scope

- Frontend UI testing  
- Performance and load testing  
- Security and penetration testing  
- Live integration testing with real AI APIs  

---

## 4. Test Levels

### 4.1 Unit Testing

Unit tests validate individual functions and classes in isolation. External dependencies such as file I/O, subprocess calls, databases, and AI APIs are mocked using `unittest.mock`.

Approximately **60 tests** fall under this category.

### 4.2 Integration Testing

Integration tests verify interactions between multiple modules such as parsing → semantic analysis → API detection → artifact storage → dependency analysis.

Approximately **3 tests**.

### 4.3 System / Environment Testing

System-level testing validates interaction with external system dependencies such as Graphviz.

Approximately **1 test**.

---

## 5. Test Types

- Functional Testing  
- Regression Testing  
- API Testing  

---

## 6. Test Environment

### 6.1 Primary Testing Tool

The only intentionally chosen and primary testing framework for this project is **pytest**.

### 6.2 Tools Used

| Tool | Usage |
|-----|------|
| pytest | Core test runner |
| pytest-django | Django integration |
| pytest-cov | Optional coverage |
| unittest.mock | Mocking |
| DRF APIClient | API testing |
| Graphviz | Optional system dependency |

---

## 7. Test Data Management

- File-based fixtures  
- Inline source code fixtures  
- Shared pytest fixtures  

---

## 8. Test Execution Strategy

```bash
pytest tests
pytest tests --cov=diagram_generator --cov-report=term-missing
```

---

## 9. Mocking Strategy

Mocking is done using Python standard library `unittest.mock`.

---

## 10. Test Coverage Summary

- **Test Files:** 32  
- **Test Methods:** 74  

---

## 11. Defect Management

Defects are tracked using standard issue tracking tools.

---

## 12. Risks

- External dependencies (Graphviz)
- AI API instability

---

**End of Document**
