# FinSense AI – Viva Preparation
## 50 Questions & Detailed Answers

---

### SECTION 1: PROJECT OVERVIEW

**Q1. What is FinSense AI?**
FinSense AI is an intelligent personal finance advisor that uses Natural Language Processing to automatically categorize expenses, Prophet time-series forecasting to predict future spending, and a rule-based financial health scoring engine to give users actionable insights about their money management.

**Q2. What problem does it solve?**
Most people track expenses in spreadsheets or not at all. FinSense AI eliminates manual categorization using NLP, predicts future spending so users can plan ahead, and gives a quantified financial health score — turning raw transaction data into actionable advice.

**Q3. What makes your project innovative?**
Three key innovations: (1) NLP-powered auto-categorization using TF-IDF + Logistic Regression trained on 55,000 Indian transactions — no manual tagging needed. (2) Facebook Prophet forecasting adapted for personal finance at the category level, not just total spend. (3) A multi-dimensional Financial Health Score (0–100) that quantifies savings ratio, budget adherence, essential vs discretionary ratio, and expense consistency in one number.

**Q4. What is the target audience?**
Working professionals and college students in India aged 18–35 who want to understand and improve their spending habits without learning complex financial tools.

**Q5. Why did you choose this project for your final year?**
It integrates the core AI/ML, full-stack, database, and software engineering skills from our B.Tech CS (AI & ML) curriculum into one deployable product. It also has strong real-world applicability and is demonstrable to recruiters.

---

### SECTION 2: TECHNOLOGY STACK

**Q6. Why FastAPI over Django or Flask?**
FastAPI is 3x faster than Flask due to async support, provides automatic OpenAPI (Swagger) documentation, has built-in Pydantic validation, and is production-ready. Django has too much overhead for a microservice-style API.

**Q7. Why PostgreSQL over MongoDB?**
Financial data is inherently relational — users have many expenses, expenses belong to budgets, scores link to months. SQL joins and ACID transactions ensure data integrity. MongoDB's flexible schema would make financial reporting harder.

**Q8. Why React.js for the frontend?**
React's component model maps perfectly to a dashboard UI (reusable chart, card, table components). It has the largest ecosystem for data visualization libraries like Chart.js and Recharts.

**Q9. What is JWT and why did you use it?**
JSON Web Token — a signed, stateless authentication token. When a user logs in, the server creates a JWT containing the user ID, signed with a secret key. The client sends it in every request header. The server verifies the signature without hitting the database. This scales better than session-based auth.

**Q10. What is bcrypt and why hash passwords?**
bcrypt is an adaptive hashing algorithm specifically designed for passwords. It adds a salt (random bytes) before hashing, making rainbow table attacks impossible. The "rounds" parameter (work factor) makes it computationally expensive, slowing down brute force attacks. We never store plain passwords.

---

### SECTION 3: NLP & MACHINE LEARNING

**Q11. How does the expense categorizer work?**
Raw merchant text (e.g. "Swiggy order biryani") goes through text cleaning → TF-IDF vectorization → Logistic Regression classification. TF-IDF converts text to numeric features weighted by term importance. Logistic Regression outputs probability scores for each of 10 categories, picking the highest.

**Q12. What is TF-IDF?**
Term Frequency–Inverse Document Frequency. TF measures how often a word appears in a document. IDF penalizes words that appear across all documents (like "the", "and"). The product TF × IDF gives high scores to distinctive, informative words — so "swiggy" scores high for Food but "payment" scores low everywhere.

**Q13. Why Logistic Regression and not a Neural Network?**
For text classification with TF-IDF features, Logistic Regression achieves 92-95% accuracy on this dataset and trains in seconds. A neural network would take minutes to train and provide marginal accuracy gains on short merchant descriptions. LR is also interpretable — you can inspect which words influence each category.

**Q14. What is the advanced approach you mentioned?**
Fine-tuning DistilBERT (distilbert-base-uncased from Hugging Face). BERT uses contextual embeddings — "I had a cold" means medicine context, not temperature. For expense categorization, DistilBERT can understand "Netflix for the month" as Entertainment even without seeing "netflix" as a keyword. Trade-off: needs GPU and 30+ minutes to fine-tune.

**Q15. How did you generate the training data?**
A synthetic data generator (`generate_dataset.py`) creates 55,000 realistic Indian transactions across 20 virtual users over 3 years. It maps categories to realistic merchant names (Swiggy → Food, Uber → Transport) with random amounts, dates, and payment modes. This avoids privacy issues with real user data.

**Q16. What is your model's accuracy?**
The TF-IDF + LR pipeline achieves approximately 92-95% accuracy on the test set (20% hold-out). Precision and recall vary by category — common categories like Food and Transport score higher than Investments which has fewer training examples.

**Q17. How do you handle unseen merchants?**
The rule-based keyword system serves as a fallback. If the trained model's confidence is below a threshold, or if no model is loaded, the system matches keywords (e.g. any text containing "apollo" → Healthcare). Unknown merchants default to "Miscellaneous" with 0.5 confidence.

**Q18. What is model persistence and how did you implement it?**
After training, the sklearn pipeline is serialized to disk using `joblib.dump()`. At server startup, `joblib.load()` deserializes it back into memory. This avoids retraining on every restart. The model file is `tfidf_lr_categorizer.pkl`.

---

### SECTION 4: TIME-SERIES FORECASTING

**Q19. What is Facebook Prophet and how does it work?**
Prophet is an additive time-series forecasting model: `y(t) = trend(t) + seasonality(t) + holidays(t) + error`. It fits a piecewise linear/logistic trend, Fourier-series-based seasonality, and holiday effects. It's robust to missing data and outliers, making it ideal for personal finance where users might not log expenses every day.

**Q20. Why Prophet over ARIMA?**
Prophet requires no manual parameter tuning (unlike ARIMA's p,d,q selection), handles multiple seasonalities automatically, is robust to missing data, and produces interpretable uncertainty intervals. ARIMA assumes stationarity and struggles with trend changes.

**Q21. Why aggregate to monthly level for forecasting?**
Daily expense data is too noisy — you might spend ₹0 one day and ₹5000 the next. Monthly aggregation removes noise and reveals genuine trends: "I spend more in December due to festivals." Prophet's yearly seasonality then captures this pattern.

**Q22. What are the confidence intervals in your forecast chart?**
yhat_lower and yhat_upper define the 80% prediction interval. This means the model is 80% confident the true value falls in this range. Wide intervals indicate high uncertainty (less data or high variance). Narrow intervals indicate consistent spending patterns.

**Q23. How much data does Prophet need?**
Minimum 2 data points, but practically needs 6+ months for meaningful seasonality detection. We show an informative error message if less than 6 months of data exists.

**Q24. What is an LSTM and how would it differ?**
Long Short-Term Memory is a Recurrent Neural Network that maintains a "memory" of past time steps using gates (input, forget, output). It can capture complex non-linear patterns but requires more data (2+ years), GPU training, and is a "black box" — harder to interpret than Prophet.

---

### SECTION 5: FINANCIAL HEALTH SCORE

**Q25. How is the Financial Health Score calculated?**
Four dimensions:
- Savings Ratio (25 pts): (income − expenses) / income × 50
- Budget Adherence (30 pts): average % of budgets not exceeded
- Essential Ratio (25 pts): essential spending / total × 35
- Expense Consistency (20 pts): month-over-month stability

These sum to a 0–100 score.

**Q26. What counts as "essential" vs "discretionary"?**
Essential: Food, Transport, Healthcare, Utilities, Education — things needed for daily life.
Discretionary: Entertainment, Shopping, Travel, Miscellaneous — things that improve life but aren't required.

**Q27. Why 30,000 as the assumed monthly income?**
It's a reasonable proxy for a fresh graduate / young professional in tier-1 Indian cities. In a production system, users would input their actual income, making the savings ratio accurate.

---

### SECTION 6: API & ARCHITECTURE

**Q28. Explain the system architecture.**
Frontend (React) → HTTP request with JWT → FastAPI Backend → SQLAlchemy ORM → PostgreSQL. ML inference happens inside the backend as Python function calls. Prophet forecasting runs on-demand per API request. All components are containerized via Docker Compose.

**Q29. What is REST and how did you follow its principles?**
Representational State Transfer — stateless HTTP APIs using standard verbs: GET (read), POST (create), PUT (update), DELETE (remove). Resources are nouns: `/expenses`, `/budgets`. HTTP status codes are meaningful: 201 (Created), 401 (Unauthorized), 404 (Not Found).

**Q30. What is SQLAlchemy ORM?**
Object-Relational Mapper — maps Python classes to database tables. Instead of writing raw SQL (`SELECT * FROM expenses WHERE user_id = 5`), you write `db.query(Expense).filter(Expense.user_id == 5)`. SQLAlchemy generates safe, parameterized SQL, preventing SQL injection.

**Q31. How do you prevent SQL injection?**
SQLAlchemy's ORM uses parameterized queries by default. User input never gets directly interpolated into SQL strings. Even manual queries use `text()` with bound parameters.

**Q32. What is rate limiting and why did you add it?**
SlowAPI applies limits (e.g. 100 requests/minute per IP) to prevent abuse — bots hammering the login endpoint, DDoS attacks. Users hitting the limit get a 429 Too Many Requests response.

**Q33. What is CORS and why is it configured?**
Cross-Origin Resource Sharing — browsers block JavaScript from calling APIs on different domains by default. The FastAPI CORSMiddleware adds headers (`Access-Control-Allow-Origin: http://localhost:3000`) to tell the browser the API accepts requests from the React app's origin.

**Q34. Explain the CSV upload endpoint.**
User uploads a bank statement CSV → FastAPI reads it with pandas → normalizes column names → iterates each row → creates Expense objects → NLP categorizes each transaction → bulk-inserts into PostgreSQL. Returns all created expenses.

---

### SECTION 7: DATABASE DESIGN

**Q35. Draw and explain your ER diagram.**
5 tables:
- `users` (id, email, username, hashed_password)
- `expenses` (id, user_id FK, amount, date, category, merchant_name)
- `budgets` (id, user_id FK, month, category, allocated_amount)
- `financial_scores` (id, user_id FK, month, score, breakdown JSON)
- All child tables reference users.id with CASCADE DELETE

**Q36. Why store category_confidence in expenses?**
It allows the UI to flag low-confidence predictions (< 0.6) with a warning, letting users correct wrong categorizations. It also enables future model improvement by identifying uncertain cases.

**Q37. Why use JSON type for breakdown in financial_scores?**
The breakdown structure (savings_ratio, budget_adherence, etc.) may evolve as we add more dimensions. Storing it as JSON avoids schema migrations every time we add a sub-score. PostgreSQL's JSONB type supports indexing and querying.

---

### SECTION 8: SECURITY

**Q38. What security measures did you implement?**
1. JWT authentication — stateless, cryptographically signed tokens
2. bcrypt password hashing — salted, adaptive cost factor
3. SQLAlchemy ORM — prevents SQL injection
4. Rate limiting (SlowAPI) — prevents brute force
5. Pydantic validation — rejects malformed input at schema level
6. HTTPS in production (Docker + nginx)
7. Environment variables for secrets (never hardcoded)

**Q39. What happens if someone steals a JWT token?**
The token is valid until expiry (60 minutes by default). Best practices: short expiry + refresh tokens, HTTPS only (prevents network interception), HttpOnly cookies (prevents XSS theft). We use Authorization headers over HTTPS.

**Q40. How would you add 2FA in the future?**
After password verification, generate a 6-digit TOTP (Time-based One-Time Password) using PyOTP and send via SMS/email. The user must submit this code within 30 seconds. Store the TOTP secret per user in the database.

---

### SECTION 9: DEPLOYMENT

**Q41. What is Docker and why did you use it?**
Docker packages the app + dependencies + OS layer into an image that runs identically anywhere. "Works on my machine" problems disappear. Docker Compose orchestrates multiple containers (backend, frontend, database) with one command: `docker compose up`.

**Q42. What is a virtual environment in Python?**
An isolated Python installation per project. `python -m venv venv` creates a fresh environment where `pip install` only affects that project. Prevents package version conflicts between different projects on the same machine.

---

### SECTION 10: TESTING

**Q43. What types of testing did you implement?**
Unit tests (security functions, NLP categorizer, health score algorithm), integration tests (API endpoints via TestClient — register, login, auth check), and schema validation tests (Pydantic rejects invalid data).

**Q44. What is pytest?**
Python's standard testing framework. `pytest tests/ -v` discovers all `test_*.py` files and runs functions starting with `test_`. It shows PASS/FAIL per test case with assertion error messages.

**Q45. What is TestClient in FastAPI testing?**
FastAPI provides `TestClient` (built on httpx) that simulates HTTP requests to the app without starting a real server. This makes API endpoint tests fast and isolated.

---

### SECTION 11: ADVANCED TOPICS

**Q46. How would you scale this to 100,000 users?**
Add Redis caching for dashboard queries. Use async SQLAlchemy (asyncpg) for non-blocking DB calls. Deploy on Kubernetes with horizontal scaling. Add a message queue (Celery + Redis) for heavy ML tasks. Use CDN for the React build.

**Q47. How would you improve the NLP model?**
Fine-tune DistilBERT on real (anonymized) transaction data. Implement active learning — flag low-confidence predictions, let users correct them, retrain periodically. Add n-gram features up to trigrams. Use ensemble of TF-IDF LR + DistilBERT.

**Q48. What is Explainable AI (XAI) and how is it relevant here?**
XAI makes ML predictions interpretable. For expense categorization, LIME (Local Interpretable Model-agnostic Explanations) could show: "This was classified as Food because of the words swiggy (weight: 0.82) and order (weight: 0.34)." This builds user trust in the AI.

**Q49. How does anomaly detection work for suspicious transactions?**
Fit a statistical baseline: mean and standard deviation of spending per category per user. Flag any transaction where `|amount - mean| > 3 × std_dev`. Isolation Forest or One-Class SVM could be trained on transaction patterns to flag structurally different transactions (unusual time, merchant, amount combo).

**Q50. What are your top 3 future enhancements?**
1. Receipt OCR — photograph a receipt → Google Cloud Vision extracts amount and merchant → auto-creates expense. 2. Voice logging — "Hey FinSense, I spent 200 on lunch" → Speech-to-Text → NLP extracts entities → creates expense. 3. Goal-based savings planner — user sets "Save ₹50,000 for laptop by December" → system recommends monthly reduction targets per category using linear programming.

---

*Good luck with your viva! — FinSense AI Team*
