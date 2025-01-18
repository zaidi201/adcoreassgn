from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGODB_DB_NAME, MONGODB_URL

client = MongoClient(MONGODB_URL)
db = client[MONGODB_DB_NAME]

class PaymentService:
    @staticmethod
    def create_payment(payment_data: dict) -> str:
        result = db["payments"].insert_one(payment_data)
        return str(result.inserted_id)

    @staticmethod
    def get_payments(filter_criteria: dict = {}, page: int = 1, limit: int = 10):
        skip = (page - 1) * limit
        payments = list(
            db["payments"]
            .find(filter_criteria)
            .skip(skip)
            .limit(limit)
        )
        for payment in payments:
            payment["_id"] = str(payment["_id"])
        return payments

    @staticmethod
    def update_payment(payment_id: str, updated_data: dict) -> bool:
        result = db["payments"].update_one({"_id": ObjectId(payment_id)}, {"$set": updated_data})
        return result.modified_count > 0

    @staticmethod
    def delete_payment(payment_id: str) -> bool:
        result = db["payments"].delete_one({"_id": ObjectId(payment_id)})
        return result.deleted_count > 0
