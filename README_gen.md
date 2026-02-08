# Living Documentation System

![Language](https://img.shields.io/badge/language-Python-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview
The Living Documentation System is a tool designed to automatically generate and maintain up-to-date documentation for software projects. It analyzes code repositories, extracts semantic information, and creates various diagrams, including class diagrams and API endpoint documentation. This system aims to simplify documentation efforts and ensure accuracy.

## Features

- **Automated Diagram Generation**: Generates class diagrams, dependency graphs, and API documentation directly from the codebase.

- **API Endpoint Detection**: Automatically discovers and documents API endpoints within Python and Java projects using frameworks like Django, FastAPI, Flask, and Spring.

- **Versioned Documentation**: Stores documentation versions associated with specific commit hashes, enabling historical documentation views.

- **Web-based Interface**: Provides a Django-based web interface for browsing projects and their associated diagrams.

- **Webhook Integration**: Supports webhook integration to trigger documentation updates automatically upon new code commits.


## Architecture
The system consists of several modules. The `api_endpoint_detector` analyzes code to identify API endpoints. The `analysis_store` houses data models for storing extracted artifacts. The Django-based `backend` provides the API and web interface, managing projects, diagrams, and webhook integrations.  Diagrams are generated server-side. `generate_docs.py` is the diagram generator.  `diagram_generator.generate_repo_diagrams` is the generator invoked by the API.

## Project Structure
```
Living-Documentation-System/
    conftest.py
    example.py
    generate_docs.py
    list_models.py
    QUICKSTART.md
    README.md
    REQUIREMENTS.md
    requirements.txt
    run_tests.py
    analysis_store/
        artifact_store.py
        models.py
    api_endpoint_detector/
        base_detector.py
        detector_manager.py
        java/
            spring_detector.py
        models/
            api_endpoint.py
        python/
            django_detector.py
            fastapi_detector.py
            flask_detector.py
    backend/
        manage.py
        requirements-dev.txt
        requirements.txt
        api/
            admin.py
            apps.py
            models.py
            poll_service.py
            serializers.py
            tests.py
            urls.py
            views.py
            __init__.py
            migrations/
                0001_initial.py
                0002_alter_project_repo_url.py
                0003_diagramimage.py
                0004_project_last_commit_hash.py
                __init__.py
        backend/
            asgi.py
            settings.py
            urls.py
            wsgi.py
            __init__.py
```

## Setup
### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Install the necessary dependencies from `requirements.txt`. 2. Configure the Django backend. 3. Create a new project via the web interface, providing the repository URL. 4. The system will automatically analyze the repository and generate initial diagrams.  Webhooks can be configured to trigger updates on commits.

## API Endpoints

- `GET /projects/`: Lists all projects.

- `POST /projects/`: Creates a new project.

- `GET /projects/{id}/`: Retrieves details of a specific project, including diagrams.

- `POST /projects/{id}/refresh/`: Triggers a refresh of the diagrams for a specific project.

- `GET /projects/{id}/history/`: Retrieves the history of diagrams for a specific project.

- `POST /webhook/commit/`: Webhook endpoint to trigger diagram generation on code commit.


## Contributing
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.