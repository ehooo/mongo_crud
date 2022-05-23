# FastApi Mongo CRUD
CRUD app for MongoDB with FastAPI

# Install
## With Docker
```
docker-compose build
```
Edit the config.env file for configure MongoDB.

## With python env
```
cd src/
pip3 install -r requirements.txt
```

## Environment vars
* ME_CONFIG_MONGODB_URL:
  URL MongoDB connection string
* DB_NAME:
  Database name on MongoDB for store collections

## Run
```
docker-compose up
```
or
```
cd src/
python3 main.py
```
or
```
cd src/
uvicorn main:app --host=0.0.0.0 --port=8000
```

Create the DB using fixtures
```
cd src/
python3 main.py --fixtures
```

## Documentation
See web documentation accessing to [/doc](http://localhost:8000/doc) or [/redoc](http://localhost:8000/redoc)

## QA
```
docker-compose exec web flake8
docker-compose exec web pytest --cov
```
or
```
cd src/
flake8
pytest --cov
```
