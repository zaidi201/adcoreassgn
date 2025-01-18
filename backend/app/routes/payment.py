from fastapi import APIRouter, HTTPException, Query
from bson.objectid import ObjectId
from app.models import Payment
from config import MONGODB_DB_NAME,MONGODB_URL
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
import os
import shutil
from pathlib import Path
from datetime import datetime
import pymongo
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DB_NAME]  # Access the "payments" database
payments_collection = db["payments"]

# Access the collection
UPLOAD_FOLDER = Path("./uploaded_files")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
router = APIRouter()

@router.post("/payments/{payment_id}/upload_evidence/")
async def upload_evidence(payment_id: str, file: UploadFile = File(...)):
    # Check if the payment exists
    payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if payment status is not 'completed'
    if payment["payee_payment_status"] != "completed":
        raise HTTPException(status_code=400, detail="Payment status must be 'completed' to upload evidence")
    
    # Ensure the file is valid (PDF, PNG, JPG)
    valid_file_types = ['pdf', 'png', 'jpg', 'jpeg']
    if file.filename.split('.')[-1].lower() not in valid_file_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, PNG, JPG are allowed.")

    # Generate a unique file name
    file_location = UPLOAD_FOLDER / f"{payment_id}_{file.filename}"
    
    # Save the file to the server
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save the file path to MongoDB (you can store it in the payment record)
    payments_collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"evidence_file": str(file_location)}}
    )

    # Return a URL or path to the uploaded file
    return {"file_path": str(file_location)}

@router.get("/payments/{payment_id}/download_evidence/")
async def download_evidence(payment_id: str):
    payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if not payment or "evidence_file" not in payment:
        raise HTTPException(status_code=404, detail="Evidence file not found for this payment")

    file_path = payment["evidence_file"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

@router.post("/payments/")
async def create_payment(payment: Payment):
    payment_data = payment.model_dump()
    result = payments_collection.insert_one(payment_data)
    return {"id": str(result.inserted_id)}

@router.get("/payments/")
async def get_payments(page: int = Query(1), limit: int = Query(10)):
    skip = (page - 1) * limit
    payments = list(
        payments_collection  
        .find({})
        .skip(skip)
        .limit(limit)
    )
    
    for payment in payments:
        # Change payment status based on due date
        current_date = datetime.now().date()
        if payment["payee_due_date"].date() == current_date:
            payment["payee_payment_status"] = "due_now"
        elif payment["payee_due_date"].date() < current_date:
            payment["payee_payment_status"] = "overdue"

        # Calculate total_due
        discount_amount = payment["due_amount"] * (payment["discount_percent"] / 100)
        tax_amount = payment["due_amount"] * (payment["tax_percent"] / 100)
        payment["total_due"] = payment["due_amount"] - discount_amount + tax_amount
        
        # Ensure _id is a string for returning it
        payment["_id"] = str(payment["_id"])

    return payments


@router.put("/payments/{payment_id}")
async def update_payment(payment_id: str, updated_payment: Payment):
    updated_data = updated_payment.model_dump()
    result = payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": updated_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment updated successfully"}

@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: str):
    result = payments_collection.delete_one({"_id": ObjectId(payment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}
