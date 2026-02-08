# Living Documentation System

An automated system that generates and maintains living architecture diagrams from your codebase. The system automatically detects code changes via Git hooks or polling and regenerates comprehensive UML diagrams including class diagrams, dependency graphs, call graphs, and API endpoint visualizations.

## Features

### 🎨 Multi-Diagram Generation
- **Class Diagrams**: Complete class hierarchies with inheritance and relationships
- **Dependency Diagrams**: Module and package dependencies
- **Call Graphs**: Function and method call relationships
- **API Diagrams**: REST API endpoints and their handlers

### 🔄 Automatic Updates
- **Git Hooks**: Local post-commit hook triggers diagram regeneration
- **Polling Service**: Background service monitors remote repositories for web-based commits
- **Version History**: Track diagram changes across commits with full history

### 🌐 Multi-Project Support
- Manage multiple repositories from a single dashboard
- Per-project diagram versioning
- Side-by-side comparison of different commits

### 🧪 Language Support
- Python (Django, Flask, FastAPI)
- Java (Spring Boot)
- Extensible parser architecture for additional languages

### 📄 AI-Powered Documentation
- Automatic README generation using Gemini
- Context-aware documentation based on project structure and code

## Architecture

### Backend (Django)
- RESTful API for project management
- Background polling service for automatic updates
- Diagram generation engine with multi-format support
- SQLite database for project and version tracking

### Frontend (Next.js)
- Modern React-based UI with real-time updates
- Interactive diagram gallery with zoom and pan
- Commit history timeline
- Project management dashboard

### Diagram Generator
- AST-based code analysis
- Semantic relationship extraction
- GraphViz DOT rendering
- Concurrent-safe generation with unique temp directories

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git
- GraphViz

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Living-Documentation-System.git
cd Living-Documentation-System
```

2. **Set up Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. **Set up Django backend**
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

4. **Set up Next.js frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Usage

### Adding a Project

1. Navigate to http://localhost:3000
2. Click "Add New Project"
3. Enter project name and Git repository URL
4. Click "Generate Initial Diagrams"

### Generating Documentation (README)

You can automatically generate a README file for your project using the built-in generator powered by Gemini.

1. **Set your API Key**:
   ```bash
   export GEMINI_API_KEY="YOUR_API_KEY"
   # On Windows PowerShell:
   # $env:GEMINI_API_KEY="YOUR_API_KEY"
   ```

2. **Run the Generator**:
   ```bash
   python generate_docs.py [OPTIONAL_API_KEY]
   ```
   
   Or to generate for a specific project programmatically:
   ```python
   from readme_manager.generator import ReadmeGenerator
   import os
   
   generator = ReadmeGenerator(project_root="/path/to/project", api_key="YOUR_KEY")
   generator.render("README.md")
   ```

### Automatic Updates

#### Option 1: Git Hook (for local commits)
Copy the post-commit hook to your repository:
```bash
cp git-hooks/post-commit /path/to/your/repo/.git/hooks/
chmod +x /path/to/your/repo/.git/hooks/post-commit
```

#### Option 2: Polling Service (for web commits)
The backend automatically polls remote repositories every 20 seconds. No configuration needed!

### Viewing Diagrams

1. Select a project from the dashboard
2. Browse diagram types (Class, Dependency, Call, API)
3. Use the version selector to view historical diagrams
4. Click diagrams to view full-size in gallery mode

### API Documentation Manager

Automatically generate, version, and enhance your API documentation.

1. **Run the Manager**:
   ```bash
   python manage_api_docs.py --framework [django|flask|fastapi] --entry [module.urls|module:app] --key [OPTIONAL_GEMINI_KEY] --pdf [OPTIONAL_OUTPUT.pdf]
   ```

2. **Features**:
   - **Extraction**: Supports Django, Flask, and FastAPI.
   - **Versioning**: Tracks added, removed, and deprecated endpoints.
   - **Enhancement**: Uses Gemini to write better endpoint descriptions.
   - **PDF Export**: Converts documentation to professional PDF format.

## Testing

### Run All Tests
```bash
export PYTHONPATH=$PYTHONPATH:./backend:.
pytest tests
```

### Run with Coverage
```bash
pytest tests --cov=diagram_generator --cov=backend/api --cov-report=term-missing
```

### Generate Test Reports
```bash
./generate_reports.sh
```

Test reports are generated in `reports/` directory with XML format for CI/CD integration.

## Project Structure

```
Living-Documentation-System/
├── backend/                 # Django backend
│   ├── api/                # REST API and models
│   ├── backend/            # Django settings
│   └── media/              # Generated diagram storage
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js app directory
│   ├── components/        # React components
│   └── public/            # Static assets
├── diagram_generator/      # Core diagram generation
│   ├── renderers.py       # GraphViz rendering
│   ├── ast_relations.py   # Relationship extraction
│   └── generate_repo_diagrams.py  # Main orchestration
├── code_parser/           # Language parsers
├── semantic_extractor/    # Semantic analysis
├── tests/                 # Comprehensive test suite
└── reports/               # Test reports (XML)
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Polling Interval

Adjust polling frequency in `backend/api/poll_service.py`:
```python
time.sleep(20)  # Poll every 20 seconds
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing Coverage

Current test coverage: **65%** for diagram_generator module

- `heuristics.py`: 100%
- `ast_relations.py`: 93%
- `repo_scanner.py`: 93%
- `ast_traverser.py`: 81%

See `TESTING_SUMMARY.md` for detailed coverage report.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with Django, Next.js, and GraphViz
- AST parsing powered by Python's `ast` module and `javalang`
- Diagram rendering via GraphViz DOT language
>>>>>>> Stashed changes
