# Sneaker Engine

A full-stack application with Angular 19 frontend and FastAPI backend.

## Project Structure

```
sneaker-engine/
├── frontend/          # Angular 19 application
├── backend/           # FastAPI application
└── README.md          # This file
```

## Prerequisites

- Node.js (v18 or higher)
- Python 3.8+
- npm or yarn

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the FastAPI server:
   ```bash
   python main.py
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm start
   ```

The app will be available at `http://localhost:4200`

## Development

### Running Both Servers

You can run both servers in separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### API Service

The Angular app includes an API service at `frontend/src/app/services/api.service.ts` that's configured to communicate with the FastAPI backend.

### Environment Configuration

- Frontend API URL is configured in `frontend/src/environments/environment.ts`
- Backend CORS is configured in `backend/main.py` to allow requests from `http://localhost:4200`

## Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`
