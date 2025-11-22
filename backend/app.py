from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from src.configs.app_config import get_app_config
from src.db.db_config import init_db
import uvicorn
from logging import getLogger

logger = getLogger(__name__)

# Initialize config
config = get_app_config()

# Initialize database FIRST before importing schema
print(f"Starting {config.application_name}...")
init_db(config, logger)

# Import schema AFTER database is initialized
from src.schemas.schema import schema

# Create FastAPI app
app = FastAPI(
    title="MyTraveller GraphQL API",
    description="Travel planning authentication service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {
        "message": "🌍 MyTraveller GraphQL API",
        "version": "1.0.0",
        "graphql": "/graphql",
        "docs": "Visit /graphql for GraphQL Playground"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mytraveller-auth",
        "environment": config.env
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )