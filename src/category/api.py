import logging
from typing import List, Union

from fastapi import (
    status,
    HTTPException,
)
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult
from starlette.responses import (
    JSONResponse,
    PlainTextResponse,
)

from category.models import (
    CategoryModel,
    SingleCategoryModel,
    ErrorMessage,
)
from db_connector import get_db


router = InferringRouter()
logger = logging.getLogger(__name__)
db_client: AsyncIOMotorClient = None


@cbv(router)
class CategoryApi:
    collection_name = "category"

    async def __insert(self, document) -> InsertOneResult:
        db = get_db()
        response = await db.seqs.find_one_and_update(
            filter={"collection": self.collection_name},
            update={"$inc": {"id": 1}},
            projection={"id": True, "_id": False},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        document["_id"] = str(response.get("id"))

        try:
            return await db[self.collection_name].insert_one(document)
        except DuplicateKeyError:
            return await self.insert_doc(document)

    async def get_all_subcategories(self, parent_id: int) -> List[CategoryModel]:
        db = get_db()
        next_parent = set()
        next_parent.add(parent_id)
        categories = []
        while next_parent:
            query = {"parent_id": {"$in": list(next_parent)}}
            next_parent = set()
            async for item in db[self.collection_name].find(query):
                item["category_id"] = item.pop("_id")
                next_parent.add(int(item["category_id"]))
                categories.append(CategoryModel(**item))
        return categories

    async def recursive_tree_lines(self, parent_id: [int] = None) -> List[str]:
        db = get_db()
        query = {"parent_id": None}
        if parent_id is not None:
            query = {"parent_id": parent_id}
        categories = []
        async for item in db[self.collection_name].find(query):
            name = item.get("name")
            for child in await self.recursive_tree_lines(parent_id=int(item.get("_id"))):
                categories.append("{}#{}".format(name, child))
            if not categories:
                categories.append(name)
        return categories

    async def disorder_tree_lines(self) -> List[str]:
        db = get_db()
        next_parent = set()
        categories = {}

        async for item in db[self.collection_name].find({"parent_id": None}):
            categories[item.get("_id")] = {
                "name": item.get("name"),
                "children": [],
            }
            next_parent.add(int(item["_id"]))

        while next_parent:
            query = {"parent_id": {"$in": list(next_parent)}}
            next_parent = set()
            async for item in db[self.collection_name].find(query):
                parent = categories[str(item.get("parent_id"))]
                parent["children"].append(item.get("_id"))
                categories[item.get("_id")] = {
                    "name": "{}#{}".format(parent["name"], item.get("name")),
                    "children": [],
                }
                next_parent.add(int(item["_id"]))

        tree_lines = [
            item["name"]
            for item in categories.values()
            if not item["children"]
        ]
        return tree_lines

    @router.get("/categories/tree")
    async def get_tree(self):
        lines = await self.recursive_tree_lines()
        return PlainTextResponse(content="\n".join(lines))

    @router.get(
        "/categories",
        response_model=List[CategoryModel],
        response_model_exclude_none=True,
        responses={
            status.HTTP_200_OK: {},
            "default": {"description": "Category list"},
        },
    )
    async def get_all(self, parent: Union[str, None] = None):
        # Because we always want return 200 OK,
        # Don"t select type for parent, in order to return from that function
        categories = []
        if parent is not None:
            try:
                categories = await self.get_all_subcategories(int(parent))
            except (ValueError, TypeError):
                return []
        else:
            db = get_db()
            async for item in db[self.collection_name].find({}):
                item["category_id"] = item.pop("_id")
                categories.append(CategoryModel(**item))
        return categories

    @router.post(
        "/categories",
        status_code=status.HTTP_201_CREATED,
        response_model=CategoryModel,
        response_model_exclude_none=True,
        responses={
            status.HTTP_201_CREATED: {},
            status.HTTP_409_CONFLICT: {
                "model": ErrorMessage,
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorMessage,
            },
            "default": {"description": "Not Found"},
        },
    )
    async def create(self, new_category: SingleCategoryModel):
        db = get_db()
        query = {"name": new_category.name}
        if new_category.parent_id:
            parent_category = await db[self.collection_name].find_one({"_id": str(new_category.parent_id)})
            if not parent_category:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"detail": "Invalid parent category"})
            query["parent_id"] = new_category.parent_id
        else:
            query["parent_id"] = {"$exists": False}
        document = await db[self.collection_name].find_one(query)
        if document:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        data = new_category.dict()
        new_category = await self.__insert(data)
        data["category_id"] = new_category.inserted_id
        return CategoryModel(**data)

    @router.get(
        "/categories/{category_id}",
        response_model=SingleCategoryModel,
        response_model_exclude_none=True,
        responses={
            status.HTTP_200_OK: {},
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorMessage,
            },
            "default": {"description": "Not Found"},
        },
    )
    async def get(self, category_id: int):
        db = get_db()
        try:
            document = await db[self.collection_name].find_one({"_id": str(category_id)})
            return SingleCategoryModel(**document)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @router.put(
        "/categories/{category_id}",
        status_code=status.HTTP_200_OK,
        response_model=SingleCategoryModel,
        response_model_exclude_none=True,
        responses={
            status.HTTP_200_OK: {},
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorMessage,
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorMessage,
            },
            "default": {"description": "Not Found"},
        },
    )
    async def update(self, category_id: int, update_category: SingleCategoryModel):
        db = get_db()
        try:
            exists = await db[self.collection_name].find_one({
                "name": update_category.name,
                "parent_id": update_category.parent_id
            })
            if exists is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)
            update_query = {"$set": {"name": update_category.name}}
            if update_category.parent_id:
                parent_category = await db[self.collection_name].find_one({"_id": str(update_category.parent_id)})
                if not parent_category:
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                        content={"detail": "Invalid parent category"})
                update_query["$set"]["parent_id"] = update_category.parent_id
            else:
                update_query["$unset"] = {"parent_id": ""}

            document = await db[self.collection_name].find_one_and_update(
                filter={"_id": str(category_id)},
                update=update_query,
                return_document=ReturnDocument.AFTER,
            )
            return SingleCategoryModel(**document)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @router.delete(
        "/categories/{category_id}",
        responses={
            status.HTTP_200_OK: {},
            status.HTTP_404_NOT_FOUND: {},
            "default": {"description": "Not Found"},
        }
    )
    async def delete(self, category_id: int):
        db = get_db()
        try:
            subcategories = await self.get_all_subcategories(category_id)
            subcategories_ids = [str(cat.category_id) for cat in subcategories]
            subcategories_ids.append(str(category_id))

            deleted = await db[self.collection_name].delete_many({"_id": {"$in": subcategories_ids}})
            if deleted.deleted_count == 0:
                return PlainTextResponse(status_code=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return PlainTextResponse(status_code=status.HTTP_404_NOT_FOUND)
        return PlainTextResponse(status_code=status.HTTP_200_OK)
