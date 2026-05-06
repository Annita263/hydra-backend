# HYDRA Backend API

Clean electrolyte hydration — FastAPI backend.

## Quick Start (do this today)

### 1. Clone & enter the project
```bash
cd hydra-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install pydantic-settings    # needed for config
```

### 4. Set up your environment variables
```bash
cp .env.example .env
# Open .env and fill in your Paystack and Resend keys
```

### 5. Create the database and seed products
```bash
python seed.py
```

### 6. Run the server
```bash
uvicorn app.main:app --reload
```

### 7. Open the interactive API docs
Visit: http://localhost:8000/docs

You'll see all endpoints. You can test them directly in the browser — no Postman needed.

---

## API Endpoints

| Method | URL | What it does |
|--------|-----|--------------|
| GET | `/` | Health check |
| POST | `/waitlist` | Join the waitlist |
| GET | `/waitlist` | See all waitlist entries |
| GET | `/products` | List CORE + ACTIVE products |
| GET | `/products/{id}` | Get one product |
| POST | `/orders` | Create an order |
| GET | `/orders` | List all orders (admin) |
| GET | `/orders/{id}` | Get one order |
| POST | `/payments/initiate/{order_id}` | Start Paystack payment |
| GET | `/payments/verify/{reference}` | Verify payment after redirect |
| POST | `/payments/webhook` | Paystack webhook (background confirm) |

---

## Purchase Flow (step by step)

```
1. POST /orders          → creates order, returns order.id
2. POST /payments/initiate/{order_id}  → returns authorization_url
3. Redirect user to authorization_url (Paystack hosted page)
4. User pays
5. Paystack redirects to GET /payments/verify/{reference}
6. Order status → "paid", confirmation email sent
```

---

## Keys you need

**Paystack** (free test account):
- Sign up at https://dashboard.paystack.com
- Go to Settings → API Keys
- Copy your test secret key (`sk_test_...`) and public key (`pk_test_...`)

**Resend** (free email sending):
- Sign up at https://resend.com
- Go to API Keys → Create API Key
- Copy the key (`re_...`)

---

## Deploying to Railway (Thursday)

1. Push this repo to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Add all your `.env` variables in Railway's Variables tab
4. Railway auto-detects FastAPI and deploys
5. Copy your Railway URL and update `BASE_URL` in the env vars

---

## Project Structure

```
hydra-backend/
├── app/
│   ├── main.py          ← FastAPI app + routers registered here
│   ├── config.py        ← reads .env variables
│   ├── database.py      ← SQLite connection + session
│   ├── models/
│   │   └── models.py    ← WaitlistEntry, Product, Order tables
│   ├── schemas/
│   │   └── schemas.py   ← request/response validation
│   ├── routers/
│   │   ├── waitlist.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   └── payments.py
│   └── utils/
│       └── email.py     ← Resend email sender
├── seed.py              ← run once to create DB + add products
├── requirements.txt
└── .env.example
```
