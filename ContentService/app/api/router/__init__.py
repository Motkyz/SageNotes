from fastapi import APIRouter

from app.api.router import note_routes, file_routes
from app.api.router import tag_routes

main_router = APIRouter()

# TODO
# main_router.include_router(note_routes, prefix="/api123")
# main_router.include_router(tag_routes, prefix="/api123")
# main_router.include_router(file_routes, prefix="/api123")