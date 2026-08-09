from fastapi import FastAPI
from database import engine, Base
from routers import auth_router, transaction_router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Expense Tracker API",
    description="Track your income and expenses with JWT authentication",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router.router)
app.include_router(transaction_router.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Expense Tracker API",
        "docs": "/docs"
    }