# FinSense AI
## Intelligent Personal Finance Advisor Using NLP and Predictive Analytics for Smart Budgeting

> **Final Year Project | B.Tech CS (AI & ML) | Jain University, Bengaluru**

---

## Overview

FinSense AI is a full-stack, AI-powered personal finance advisor that automatically categorizes expenses using NLP, forecasts future spending with Facebook Prophet, and generates a personalized Financial Health Score — all wrapped in a modern React dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js 18, Tailwind CSS, Chart.js |
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Database | PostgreSQL 15 |
| ML – NLP | TF-IDF + Logistic Regression, DistilBERT |
| ML – Forecast | Facebook Prophet, LSTM (TensorFlow) |
| Auth | JWT (python-jose), bcrypt |
| Deployment | Docker, Docker Compose |

---

## Features

- **Auto expense categorization** – NLP model classifies merchants into 10 categories with 92%+ accuracy
- **CSV bank statement import** – Upload your bank export and auto-parse all transactions
- **Time-series forecasting** – Prophet predicts next 1–12 months of spending per category
- **Financial Health Score** – 0–100 score across savings, budget adherence, and spending patterns
- **Budget management** – Set category limits, see real-time utilisation bars
- **AI chat assistant** – Ask questions about your spending in plain English
- **Interactive dashboard** – Donut charts, bar charts, forecast line charts

---

## Quick Start

```bash
# With Docker (easiest)
docker compose up --build

# Without Docker
# Terminal 1: Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm install && npm start
```

Full setup instructions: **[SETUP_GUIDE.md](SETUP_GUIDE.md)**

---

## Project Structure

```
FinSense-AI/
├── frontend/               React app
│   ├── src/pages/          Dashboard, Expenses, Budgets, Forecast, Chat
│   ├── src/utils/api.js    Axios API client
│   └── src/context/        Auth state management
├── backend/                FastAPI server
│   ├── app/api/v1/         REST endpoints
│   ├── app/models/         SQLAlchemy ORM
│   ├── app/services/       NLP, Forecasting, Health Score, Chat
│   └── app/core/           Config, DB, Security
├── ml/
│   ├── generate_dataset.py 55,000 synthetic transactions
│   ├── train_categorizer.py TF-IDF + LR training
│   ├── bert_trainer.py     DistilBERT fine-tuning
│   └── lstm_forecaster.py  LSTM time-series model
├── docs/VIVA_QA.md         50 viva Q&A
├── SETUP_GUIDE.md          Complete install guide
└── docker-compose.yml
```

---

## ML Models

### Expense Categorizer
- **Primary**: TF-IDF (bigrams, 30k features) + Logistic Regression → ~93% accuracy
- **Advanced**: DistilBERT fine-tuned → ~96% accuracy (GPU recommended)
- Trained on 55,000 synthetic Indian transactions across 10 categories

### Expense Forecaster
- **Primary**: Facebook Prophet (additive decomposition, yearly seasonality)
- **Advanced**: LSTM (64→32 units, 3-month lookback window)
- Operates at monthly aggregation level per user/category

---

## API Documentation

Start the backend then visit: **http://localhost:8000/docs**

Key endpoints:
- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT token
- `GET/POST /api/v1/expenses` — CRUD expenses
- `POST /api/v1/expenses/upload/csv` — Import bank statement
- `GET /api/v1/dashboard` — Full dashboard data
- `GET /api/v1/forecast` — Prophet forecast
- `POST /api/v1/health-score` — Compute financial health
- `POST /api/v1/chat` — AI chat assistant

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Three Innovative Features

1. **NLP Auto-Categorization** — Zero manual tagging. Merchant names are classified in real-time.
2. **Category-Level Forecasting** — Not just total spend, but per-category predictions (e.g., "Your Food spend will be ₹8,200 next month").
3. **Quantified Financial Health Score** — A single 0–100 number that replaces vague advice with measurable progress.

---

## Authors

Varish Gada | B.Tech CS AI & ML | Jain University | 2027

GitHub: [varish05](https://github.com/varish05) · LinkedIn: [varish-gada](https://linkedin.com/in/varish-gada)
