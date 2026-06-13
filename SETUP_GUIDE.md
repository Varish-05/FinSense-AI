# FinSense AI – Complete Setup Guide
## From Zero to Running on Your Laptop (Windows/macOS/Linux)

---

## PART 1: WHAT YOU NEED TO INSTALL (One-Time Setup)

### Step 1 – Install Python 3.11

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11.x (NOT 3.12+, Prophet needs 3.11)
3. Run installer → CHECK "Add Python to PATH" → Install Now
4. Open Command Prompt and verify: `python --version`

**macOS:**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11
python3.11 --version
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
python3.11 --version
```

---

### Step 2 – Install Node.js 20

**Windows/macOS:**
1. Go to https://nodejs.org
2. Download "LTS" version (v20.x)
3. Run installer with all defaults
4. Verify: `node --version` and `npm --version`

**Ubuntu/Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
node --version
npm --version
```

---

### Step 3 – Install PostgreSQL

**Windows:**
1. Go to https://www.postgresql.org/download/windows/
2. Download and install PostgreSQL 15
3. Set password for `postgres` user (remember it!)
4. Keep default port 5432

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Linux:**
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### Step 4 – Install Git

**Windows:** https://git-scm.com/download/win → install with defaults
**macOS:** `brew install git`
**Linux:** `sudo apt install git -y`

---

### Step 5 – Install Docker (OPTIONAL – for container deployment)

Go to https://docs.docker.com/get-docker/ and install Docker Desktop.
This is OPTIONAL for development – you can run without Docker.

---

## PART 2: SET UP THE DATABASE

### Create the database

**Windows (open pgAdmin or Command Prompt):**
```cmd
psql -U postgres
```

**macOS/Linux:**
```bash
sudo -u postgres psql
```

Then in the psql shell:
```sql
CREATE USER finsense_user WITH PASSWORD 'finsense_pass';
CREATE DATABASE finsense OWNER finsense_user;
GRANT ALL PRIVILEGES ON DATABASE finsense TO finsense_user;
\q
```

---

## PART 3: SET UP THE BACKEND

Open a terminal/command prompt.

```bash
# 1. Navigate to the project
cd FinSense-AI/backend

# 2. Create a virtual environment
python3.11 -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies (this takes 5-10 minutes)
pip install -r requirements.txt

# 5. Copy the environment file
cp .env .env.local
# Edit .env with your actual DB password if different

# 6. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Open http://localhost:8000/docs to see the API documentation (Swagger UI).

---

## PART 4: TRAIN THE NLP MODEL

Open a NEW terminal (keep backend running).

```bash
cd FinSense-AI

# Activate the same venv
source backend/venv/bin/activate   # Linux/macOS
# OR: backend\venv\Scripts\activate  # Windows

# Step 1: Generate the 55,000-transaction dataset
python ml/generate_dataset.py
# Output: ml/data/transactions.csv

# Step 2: Train the TF-IDF + Logistic Regression model
python ml/train_categorizer.py
# Output: ml/models/tfidf_lr_categorizer.pkl
# Expected accuracy: ~92-95%

# Step 3: Copy the model where the backend can find it
cp ml/models/tfidf_lr_categorizer.pkl backend/ml_models/
```

---

## PART 5: SET UP THE FRONTEND

Open another terminal.

```bash
# 1. Navigate to frontend
cd FinSense-AI/frontend

# 2. Install Node packages (takes 2-3 minutes)
npm install

# 3. Start the React development server
npm start
```

Browser should open automatically at http://localhost:3000

---

## PART 6: RUNNING THE COMPLETE APP

Keep these 2 terminals running simultaneously:

| Terminal | Command | URL |
|----------|---------|-----|
| Backend  | `uvicorn app.main:app --reload` | http://localhost:8000 |
| Frontend | `npm start` | http://localhost:3000 |

### First-time usage:
1. Open http://localhost:3000
2. Click "Create account" → fill in your details
3. Log in
4. Go to Expenses → Add some expenses
5. Dashboard will show your spending breakdown
6. Go to Forecast (need 6+ months of data)
7. Go to AI Chat → ask questions about your spending

---

## PART 7: DOCKER DEPLOYMENT (Easiest Way to Run Everything)

If Docker is installed:

```bash
cd FinSense-AI
docker compose up --build
```

This starts PostgreSQL + Backend + Frontend automatically.
Wait ~3 minutes for first build. Then open http://localhost:3000

---

## PART 8: RUN TESTS

```bash
cd FinSense-AI/backend
source venv/bin/activate
pytest tests/ -v
```

---

## PART 9: PROJECT FOLDER EXPLAINED

```
FinSense-AI/
├── frontend/               ← React.js app (what users see)
│   ├── src/
│   │   ├── pages/          ← Dashboard, Expenses, Chat, etc.
│   │   ├── components/     ← Reusable UI parts
│   │   ├── utils/api.js    ← All API calls to backend
│   │   └── context/        ← Global login state
│   └── package.json
│
├── backend/                ← FastAPI Python server
│   ├── app/
│   │   ├── main.py         ← App entry point
│   │   ├── api/v1/         ← All REST endpoints
│   │   ├── models/         ← Database tables
│   │   ├── schemas/        ← Request/response validation
│   │   ├── services/       ← Business logic + ML
│   │   └── core/           ← Config, DB, Security
│   ├── requirements.txt
│   └── tests/              ← Pytest tests
│
├── ml/                     ← ML model training code
│   ├── generate_dataset.py ← Creates 55k transactions
│   ├── train_categorizer.py← Trains NLP model
│   ├── data/               ← CSV datasets
│   └── models/             ← Saved .pkl model files
│
└── docker-compose.yml      ← Runs everything with one command
```

---

## PART 10: COMMON ERRORS & FIXES

### "Port 8000 already in use"
```bash
# Kill whatever is using it
# Linux/macOS:
lsof -ti:8000 | xargs kill
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### "Module not found" errors
```bash
# Make sure venv is activated!
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                 # macOS
# Check Services panel             # Windows
```

### React won't start
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

---

## PART 11: DEMO GUIDE FOR EVALUATION

1. Show the **Login/Register** screen → explain JWT security
2. Add 5-6 expenses with different merchants → show **NLP auto-categorization**
3. Open **Dashboard** → explain the charts and stats
4. Set budgets → show **budget utilization bars**
5. Go to **Forecast** → explain Prophet model
6. Open **AI Chat** → ask "What is my highest spending category?"
7. Open http://localhost:8000/docs → show the **full REST API**
8. Show the `/health-score` endpoint → explain the scoring algorithm

---

## OPTIONAL: Add Anthropic API for better chat

If you have an Anthropic API key, add it to `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Then restart the backend. The AI chat will use Claude claude-sonnet-4-20250514.

---

## Summary: Minimum commands to run the project

```bash
# Terminal 1 - Backend
cd FinSense-AI/backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd FinSense-AI/frontend && npm start
```
