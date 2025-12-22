text
# 🤖 AI Test Generator

Convert plain‑language software requirements into structured test cases using an AI backend (FastAPI + OpenAI) and a simple web UI.

---

## 1. Files in this project

test/
├─ backend/
│ ├─ main.py # FastAPI API server
│ ├─ .env # OpenAI API key (you create this)
├─ frontend/
│ ├─ index.html # Web UI
├─ requirements.txt # Python dependencies
└─ README.md # This file

text

---

## 2. One‑time setup (first time on a machine)

Open a terminal and run:

1. Go to project folder
cd ~/Desktop/test

text

### 2.1. Create virtual environment

Create venv (only once)
python -m venv .venv

text

### 2.2. Activate virtual environment (every new terminal)

macOS / Linux:
source .venv/bin/activate

Windows PowerShell:
.venv\Scripts\Activate.ps1
Windows CMD:
.venv\Scripts\activate
text

You should see `(.venv)` at the start of the terminal prompt.

### 2.3. Install Python dependencies from `requirements.txt`

cd ~/Desktop/test
source .venv/bin/activate

pip install -r requirements.txt

text

---

## 3. Configure OpenAI API key

You need an API key from OpenAI.

1. Go to: https://platform.openai.com/api/keys  
2. Create a new secret key and copy it.

Create/update the `.env` file in `backend`:

cd ~/Desktop/test/backend
touch .env

text

Open `.env` and put:

OPENAI_API_KEY=sk-xxxxx_your_actual_key_here

text

---

## 4. How to run the project (every time)

You always use **two terminals**: one for backend, one for frontend.

### 4.1. Terminal 1 – run backend (FastAPI + Uvicorn)

Go to project root
cd ~/Desktop/test

Activate venv
source .venv/bin/activate

Start backend
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

text

You should see:

INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete

text

Leave this terminal **running**.

---

### 4.2. Terminal 2 – run frontend (simple HTTP server)

Open a **new** terminal window:

cd ~/Desktop/test

Optional but OK:
source .venv/bin/activate

cd frontend
python -m http.server 8002

text

You should see:

Serving HTTP on :: port 8002 (http://[::]:8002/) ...

text

Leave this terminal **running**.

---

### 4.3. Open the app in your browser

Open this URL:

http://localhost:8002

text

You should see:

- Purple gradient page  
- “AI Test Generator” title  
- Requirements textarea  
- Status card with “✅ API Connected”  
- “Test Cases” section  

---

## 5. How to use the app

1. In **Requirements** box, paste something like:

Login Feature:

User can log in with email and password

Email must be valid format

Password must be at least 8 characters

Show error on invalid email

Show error on short password

On successful login, redirect to dashboard

text

2. Select a **Test Type**:
- Functional Tests  
- Comprehensive (Functional + Boundary + Negative)  
- Boundary Tests  

3. Click **Generate Tests**.

4. Wait a few seconds. Test cases appear under **Test Cases** with:
- ID  
- Title  
- Preconditions  
- Steps  
- Expected Result  

Use **Clear** to reset and try new requirements.

---

## 6. Common problems and fixes

### 6.1. “API Not Connected – Start backend on port 8000”

The backend server is not running.

Fix:

cd ~/Desktop/test
source .venv/bin/activate
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

text

Refresh `http://localhost:8002`.

### 6.2. Port already in use (OSError: [Errno 48])

Something else is using that port.

Check and kill:

lsof -i :8002
kill -9 <PID>

text

Or run on a different port:

cd ~/Desktop/test/frontend
python -m http.server 8003

text

Then open: `http://localhost:8003`

---

## 7. Reinstalling dependencies

If dependencies break or you move the project:

cd ~/Desktop/test
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

text

---

## 8. Quick start summary

Every time you want to use the app:

Terminal 1 (backend)
cd ~/Desktop/test
source .venv/bin/activate
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

text
undefined
Terminal 2 (frontend)
cd ~/Desktop/test
source .venv/bin/activate
cd frontend
python -m http.server 8002

text

Then open in browser:

http://localhost:8002

text
undefined