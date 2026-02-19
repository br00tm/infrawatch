"""Base repository with common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[T]):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.model = model

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new document."""
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model.from_mongo(data)

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get a document by ID."""
        if not ObjectId.is_valid(id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            return self.model.from_mongo(doc)
        return None

    async def get_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None,
    ) -> List[T]:
        """Get all documents with optional filtering and pagination."""
        filter = filter or {}
        cursor = self.collection.find(filter).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        docs = await cursor.to_list(length=limit)
        return [self.model.from_mongo(doc) for doc in docs]

    async def count(self, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching the filter."""
        filter = filter or {}
        return await self.collection.count_documents(filter)

    async def update(
        self,
        id: str,
        data: Dict[str, Any],
    ) -> Optional[T]:
        """Update a document by ID."""
        if not ObjectId.is_valid(id):
            return None
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True,
        )
        if result:
            return self.model.from_mongo(result)
        return None

    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def delete_many(self, filter: Dict[str, Any]) -> int:
        """Delete multiple documents matching the filter."""
        result = await self.collection.delete_many(filter)
        return result.deleted_count

    async def exists(self, filter: Dict[str, Any]) -> bool:
        """Check if a document exists."""
        doc = await self.collection.find_one(filter, {"_id": 1})
        return doc is not None
