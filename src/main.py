import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from category.api import router as category_router
from db_connector import (
    shutdown_db_client,
    create_db_client,
    get_db,
)
from handlers import validation_exception_handler


app = FastAPI(
    docs_url="/doc",
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_event_handler("startup", create_db_client)
app.add_event_handler("startup", shutdown_db_client)

app.include_router(category_router, prefix="/api/v1")


if __name__ == "__main__":
    import argparse
    import asyncio
    import json
    import uvicorn

    import db_connector

    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(description='MongoDB CRUD')
    parser.add_argument('--fixtures', action='store_true')
    options = parser.parse_args()
    if options.fixtures:
        db = get_db()
        with open(os.path.join(CURRENT_PATH, "category/tests/fixtures.json")) as f:
            items = json.load(f)
            asyncio.run(db_connector.create_bulk_async(items, db))
        print("Fixtures applied")
        exit()

    reload = "--reload" in os.environ.get("API_ARGS", "")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)
