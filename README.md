# Django Backend Server

This is the backend server for the DocAI application built with Django and Django REST Framework.

## Quick Start

### Option 1: Using the startup scripts (Recommended)

**For macOS/Linux:**
```bash
./start_server.sh
```

**For Windows:**
```cmd
start_server.bat
```

### Option 2: Manual startup

1. Navigate to the backend directory:
```bash
cd ai-document-backend
```

2. (Optional) Activate virtual environment if you have one:
```bash
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate.bat  # On Windows
```

3. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

4. Run migrations:
```bash
python3 manage.py migrate
```

5. Start the server:
```bash
python3 manage.py runserver
```

## Server Information

- **Default URL:** http://127.0.0.1:8000/
- **Framework:** Django 5.2.1 with Django REST Framework
- **Database:** SQLite (db.sqlite3)
- **Authentication:** JWT tokens

## Features

- Document upload and management
- AI-powered document analysis
- RESTful API endpoints
- JWT authentication
- CORS enabled for frontend integration

## Environment Variables

Create a `.env` file in the root directory with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
```

## API Endpoints

The server provides various endpoints for document management and AI analysis. Once running, you can access the API at http://127.0.0.1:8000/

## Stopping the Server

Press `CTRL+C` in the terminal to stop the development server.