from motor.motor_asyncio import AsyncIOMotorDatabase


async def fetch_concepts(db: AsyncIOMotorDatabase):
    """
    List all concepts in the database
    
    Results limited to 1000 records
    """
    return await db.concepts.find().to_list(length=1000)
