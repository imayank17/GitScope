# GitScope

[![GitScope CI/CD Pipeline](https://github.com/imayank17/GitScope/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/imayank17/GitScope/actions/workflows/ci-cd.yml)

## How to Run the Project

Follow the steps below to set up and run the project locally.

## 1. Create a `.env` File

Create a `.env` file in the project root and add the following environment variables:

```env
APP_NAME=YOUR_APP_NAME
APP_VERSION=YOUR_APP_VERSION
DEBUG=TRUE/FALSE
DATABASE_URL=YOUR_DATABASE_URL
SECRET_KEY=replace_this_with_a_long_random_secret_key
ALGORITHM=YOUR_HASHING_ALGO
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
GITHUB_TOKEN=YOUR_GITHUB_TOKEN
```

## 2. Navigate to the Backend Directory

```bash
cd backend
```

## 3. Create a Virtual Environment

```bash
python3 -m venv venv
```

## 4. Activate the Virtual Environment

**Linux/macOS**

```bash
source venv/bin/activate
```

**Windows (Command Prompt)**

```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

## 5. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## 6. Start the Development Server

Run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc