# Living Documentation System - Quick Start

## Prerequisites

### Backend
- Python 3.12+
- Graphviz (system package)

### Frontend
- Node.js 18+
- npm 9+

## Quick Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv graphviz
```

**macOS:**
```bash
brew install python graphviz
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations
cd backend
python manage.py migrate

# Start server
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Project Structure

```
Living-Documentation-System/
├── backend/                    # Django backend
│   ├── api/                   # REST API endpoints
│   ├── backend/               # Django settings
│   ├── requirements.txt       # Python dependencies
│   └── requirements-dev.txt   # Development dependencies
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js app directory
│   ├── package.json           # Node dependencies
│   └── ...
├── code_parser/               # Code parsing utilities
├── diagram_generator/         # Diagram generation logic
├── semantic_extractor/        # Code analysis
├── requirements.txt           # Root Python dependencies
└── REQUIREMENTS.md            # Detailed requirements documentation
```

## Available Commands

### Backend
```bash
python manage.py runserver     # Start dev server
python manage.py migrate       # Run migrations
pytest                         # Run tests
black .                        # Format code
pylint **/*.py                 # Lint code
```

### Frontend
```bash
npm run dev                    # Start dev server
npm run build                  # Build for production
npm run lint                   # Lint code
npm run format                 # Format code
npm run type-check             # Check types
```

## Next Steps

1. Review `REQUIREMENTS.md` for detailed documentation
2. Configure environment variables (see REQUIREMENTS.md)
3. Start developing!

## Troubleshooting

See the **Troubleshooting** section in `REQUIREMENTS.md` for common issues and solutions.
