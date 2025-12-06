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
- PostgreSQL

## Database Setup

1. Start PostgreSQL:
   ```bash
   sudo service postgresql start
   ```

2. Create the database:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE sneaker_engine;
   CREATE USER sneaker_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE sneaker_engine TO sneaker_user;
   \q
   ```

3. Create a `.env` file in the `backend` directory with your database credentials:
   ```
   DATABASE_URL=postgresql://sneaker_user:your_password@localhost/sneaker_engine
   ```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. **Optional: Automatic venv activation**
   
   The backend directory includes a `.envrc` file for automatic virtual environment activation using `direnv`.
   
   To enable this:
   ```bash
   # Install direnv
   sudo apt install direnv  # Ubuntu/Debian
   # brew install direnv    # macOS
   
   # Add to your ~/.bashrc or ~/.zshrc
   eval "$(direnv hook bash)"  # for bash
   # eval "$(direnv hook zsh)" # for zsh
   
   # Allow direnv in the backend directory
   cd backend
   direnv allow
   ```
   
   Now the venv will automatically activate when you enter the backend directory!

6. Run the FastAPI server:
   ```bash
   python3 main.py
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
