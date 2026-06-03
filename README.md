# Quantara

**Live → [getquantara.vercel.app](https://getquantara.vercel.app)**

An RBI interest rate path simulator. Given the current repo rate, Quantara runs 10,000 Monte Carlo simulations using the Vasicek and CIR stochastic models and answers three practical questions:

- **Home loan borrowers:** What will my EMI look like in the best, median, and worst rate scenarios 12 months from now?
- **Bond investors:** How does my bond price shift across simulated rate endpoints? What is my actual duration exposure?
- **Analysts and CFOs:** What are statistically grounded rate scenarios for planning models and stress tests?

---

## Models

### Vasicek (1977)

```
dr = κ(θ − r)dt + σ dW
```

Mean-reverting Ornstein–Uhlenbeck process. Admits negative rates (useful for stress tests). Closed-form bond pricing via:

```
P(t,T) = A(t,T) · exp(−B(t,T) · r_t)
B(t,T) = (1 − e^{−κ(T−t)}) / κ
A(t,T) = exp((θ − σ²/2κ²)(B − (T−t)) − σ²B²/4κ)
```

### CIR (Cox–Ingersoll–Ross, 1985)

```
dr = κ(θ − r)dt + σ√r dW
```

Non-negative rates guaranteed when the Feller condition holds: `2κθ > σ²`. Volatility scales with the rate level, making it more empirically accurate for emerging market central bank rates. Exact simulation uses non-central chi-squared transitions.

---

## Calibration

Parameters κ (mean reversion), θ (long-run mean), and σ (volatility) are estimated via Maximum Likelihood Estimation on daily forward-filled RBI repo rate data from 2011 to present. The discrete-time conditional distributions are:

- **Vasicek:** `r_{t+1} | r_t ~ N(μ, v)` where `μ = r_t e^{−κΔt} + θ(1 − e^{−κΔt})` and `v = σ²(1 − e^{−2κΔt}) / 2κ`
- **CIR:** Euler approximation of the non-central chi-squared conditional

Calibration runs on startup and refreshes every 24 hours. If convergence fails, the model falls back to `κ=0.30, θ=6.50, σ=0.80` with a warning in the API response.

---

## Performance

| Operation | Target | Notes |
|---|---|---|
| 10,000-path simulation | < 2s | Vectorised NumPy, no Python loops |
| API response (cache miss) | < 3s | Includes simulation + serialisation |
| API response (cache hit) | < 100ms | Redis, 1-hour TTL |
| Calibration | < 5s | L-BFGS-B optimiser |

---

## Stack

**Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy (async), PostgreSQL, Redis, NumPy, SciPy, APScheduler

**Frontend:** SvelteKit 2, Svelte 5, TypeScript, Tailwind CSS v4, Apache ECharts

**Infrastructure:** Docker Compose (local), Railway (backend), Vercel (frontend)

---

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres + Redis
cd ../docker
docker compose up -d db redis

# Run the API
cd ../backend
cp ../.env.example .env
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend available at `http://localhost:5173`.

### Full stack with Docker

```bash
cd docker
docker compose up
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/rates/historical` | Historical RBI repo rate series |
| POST | `/api/v1/simulate/vasicek` | Vasicek Monte Carlo simulation |
| POST | `/api/v1/simulate/cir` | CIR Monte Carlo simulation |
| POST | `/api/v1/simulate/compare` | Both models side-by-side |
| GET | `/api/v1/calibrate/{model}` | Return calibrated κ, θ, σ |
| POST | `/api/v1/emi/impact` | EMI distribution from simulated paths |
| POST | `/api/v1/bond/price` | Bond price distribution |
| GET | `/api/v1/health` | Health check |

Simulation request body:

```json
{
  "current_rate": 5.75,
  "horizon_months": 12,
  "n_paths": 10000,
  "use_calibrated": true
}
```

---

## Deployment

### Backend (Railway)

Set environment variables in Railway dashboard:
```
DATABASE_URL
REDIS_URL
FRED_API_KEY
```

### Frontend (Vercel)

```
VITE_API_URL=https://your-railway-backend.railway.app
```
