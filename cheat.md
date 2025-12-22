text
# ⚡ AI Test Generator – Quick Run Cheat Sheet

Minimal step‑by‑step guide with **all commands** you need every time you use this project.

---

## 0. Open terminal and go to project

cd ~/Desktop/test

text

If you are not sure where you are:

pwd # should show /Users/<you>/Desktop/test
ls # should show backend, frontend, .venv, README.md, etc.

text

---

## 1. Activate virtual environment

Do this in **every new terminal window** before running backend or frontend.

macOS / Linux
cd ~/Desktop/test
source .venv/bin/activate

text

Check it is active:

which python # should show .../Desktop/test/.venv/bin/python

text

If you ever want to deactivate:

deactivate

text

---

## 2. Start BACKEND (API server) – Terminal 1

Open **Terminal 1** and run:

cd ~/Desktop/test
source .venv/bin/activate

cd backend
ls # should show main.py and .env

Run FastAPI with Uvicorn
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

text

You should see lines like:

INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete

text

**Health check (optional):**

Open a new tab in your browser and go to:

http://127.0.0.1:8000

text

or from another terminal:

curl http://127.0.0.1:8000

text

Expected output (similar to):

{"message":"✅ AI Test Generator API is running!","version":"1.0","status":"healthy"}

text

Leave **Terminal 1** running.

---

## 3. Start FRONTEND (static server) – Terminal 2

Open **Terminal 2** and run:

cd ~/Desktop/test
source .venv/bin/activate # optional but OK

cd frontend
ls # should show index.html

Start simple HTTP server on port 8002
python -m http.server 8002

text

You should see:

Serving HTTP on :: port 8002 (http://[::]:8002/) ...

text

Leave **Terminal 2** running.

---

## 4. Open the web app in browser

In your browser (Brave/Chrome/etc.) open:

http://localhost:8002

and then open ur index.html in browser



if 
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
INFO:     Will watch for changes in these directories: ['/Users/yashdhole/Desktop/test/backend']
ERROR:    [Errno 48] Address already in use. 
this kind of error occirs do

1. Find and kill the old process
In a terminal:

bash
lsof -i :8000
You’ll see something like:

text
python  12345 yashdhole   ()...  TCP 127.0.0.1:8000 (LISTEN) do not type this)
Kill it (replace 12345 with your PID):

bash
kill -9 12345
Check it’s gone:

bash
lsof -i :8000
# should show nothing