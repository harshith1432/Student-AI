# System Architecture - Student AI

## High-Level Overview
Student AI is built on a modular Flask architecture, separating concerns between routes, models, and specialized services.

## Components

### 1. Web Layer (Flask)
- **Blueprints**: Used to compartmentalize logic.
  - `auth_routes.py`: Handles user registration, login, and session management.
  - `task_routes.py`: Manages AI task requests, history retrieval, and file exports.
  - `admin_routes.py`: Provides statistics and management tools for administrators.
- **Middleware**: Flask-Login for session security and Flask-WTF for CSRF protection.

### 2. Service Layer
- **AI Service (`ai_service.py`)**: Interfaces with HuggingFace Inference API. Implements personality-driven system prompts and task-specific instructions.
- **Export Service (`export_service.py`)**: Handles multi-format document generation.
  - `PDF`: Uses `xhtml2pdf` for standard academic formatting.
  - `Handwritten PDF`: Uses `reportlab` with custom TTF fonts to simulate a student's handwriting.
  - `DOCX`: Uses `python-docx` for editable professional formats.

### 3. Data Layer (PostgreSQL)
- **ORM**: SQLAlchemy is used for object-relational mapping.
- **Connection Management**: Implements connection pooling and recycling to maintain stability with cloud-hosted databases (e.g., Neon).
- **Models**:
  - `User`: Authentication and profile data.
  - `Task`: User prompts and task metadata.
  - `AIResponse`: Historical AI-generated content linked to tasks.
  - `UsageLog`: Metrics and token tracking.

## Deployment Strategy
- **Web Server**: Gunicorn/Waitress for production runtime.
- **Security**: Rate limiting via Flask-Limiter.
- **Environment**: Strict separation of credentials via `.env` files.
