# Living Documentation System - Requirements

This document describes the dependencies and requirements for both the Frontend and Backend of the Living Documentation System.

## Backend Requirements

### System Requirements
- **Python**: 3.12 or higher
- **Graphviz**: Required for diagram generation (system package)
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - macOS: `brew install graphviz`
  - Windows: Download from [graphviz.org](https://graphviz.org/download/)

### Python Dependencies

Install all Python dependencies using:
```bash
pip install -r backend/requirements.txt
```

#### Core Framework
- **Django 6.0.1**: Web framework for the backend API
- **djangorestframework 3.15.2**: RESTful API framework
- **django-cors-headers 4.6.0**: Handle Cross-Origin Resource Sharing

#### File Handling
- **Pillow 11.0.0**: Image processing for diagram files

#### Diagram Generation
- **graphviz 0.20.3**: Python interface to Graphviz

#### Development & Testing
- **pytest 8.3.4**: Testing framework
- **pytest-django 4.9.0**: Django integration for pytest
- **pytest-cov 6.0.0**: Code coverage plugin
- **coverage 7.6.9**: Code coverage measurement

#### Code Quality
- **pylint 3.3.2**: Python linter
- **black 24.10.0**: Code formatter
- **flake8 7.1.1**: Style guide enforcement
- **mypy 1.13.0**: Static type checker

#### Utilities
- **python-dotenv 1.0.1**: Environment variable management

### Optional Dependencies
For production deployment with PostgreSQL:
```bash
pip install psycopg2-binary==2.9.9
```

---

## Frontend Requirements

### System Requirements
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)

### JavaScript/TypeScript Dependencies

Install all frontend dependencies using:
```bash
cd frontend
npm install
```

#### Core Framework
- **Next.js 14.1.0**: React framework for production
- **React 18.3.1**: UI library
- **React DOM 18.3.1**: React rendering for web

#### UI Components
- **lucide-react 0.300.0**: Icon library

#### Styling
- **Tailwind CSS 3.4.1**: Utility-first CSS framework
- **PostCSS 8.4.35**: CSS transformation tool
- **Autoprefixer 10.4.17**: CSS vendor prefixing

#### Development Tools
- **TypeScript 5.6.3**: Static type checking
- **ESLint 8.57.1**: JavaScript/TypeScript linter
- **eslint-config-next 14.1.0**: Next.js ESLint configuration
- **Prettier 3.4.2**: Code formatter

#### Type Definitions
- **@types/node**: TypeScript definitions for Node.js
- **@types/react**: TypeScript definitions for React
- **@types/react-dom**: TypeScript definitions for React DOM

---

## Installation Guide

### Backend Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install graphviz python3-dev

   # macOS
   brew install graphviz
   ```

3. **Install Python packages**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run migrations**:
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Build for production** (optional):
   ```bash
   npm run build
   npm start
   ```

---

## Development Scripts

### Backend
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Run database migrations
- `python manage.py test` - Run Django tests
- `pytest` - Run pytest tests
- `pytest --cov` - Run tests with coverage
- `black .` - Format code
- `pylint **/*.py` - Lint Python code
- `mypy .` - Type check

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues
- `npm run type-check` - Check TypeScript types
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

---

## Environment Variables

### Backend (.env)
Create a `.env` file in the backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend Issues

**Graphviz not found:**
- Ensure Graphviz is installed system-wide
- Verify with: `dot -V`

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r backend/requirements.txt`

**Database errors:**
- Run migrations: `python manage.py migrate`
- Delete `db.sqlite3` and re-run migrations if needed

### Frontend Issues

**Module not found:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**Build errors:**
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run build`

**Type errors:**
- Run type check: `npm run type-check`
- Update type definitions if needed

---

## Version Compatibility

This project has been tested with:
- Python 3.12+
- Node.js 18.x and 20.x
- Django 6.0.1
- Next.js 14.1.0

For best results, use the exact versions specified in the requirements files.
