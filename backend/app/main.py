from fastapi import FastAPI
from app.routes.payment import router as payment_router

app = FastAPI()

# Register routes
app.include_router(payment_router, prefix="/api", tags=["Payments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Payment Management API"}
