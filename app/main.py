from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import waitlist, products, orders, payments, auth, cart

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for HYDRA — clean daily electrolyte hydration.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(waitlist.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "product": "HYDRA API", "version": "0.1.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}