from motor.motor_asyncio import AsyncIOMotorClient
import os

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client.get_database(os.getenv("MONGO_DB"))
