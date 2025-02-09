from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api import api_route


def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # List of allowed origins
        allow_credentials=True,
        allow_methods=["*"],  # List of allowed methods
        allow_headers=["*"],  # List of allowed headers
    )
    app.include_router(api_route, prefix='/api/v1')

    return app
