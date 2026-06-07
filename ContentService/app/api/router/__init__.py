from fastapi import APIRouter

from app.api.router import note_routes, file_routes
from app.api.router import tag_routes

main_router = APIRouter()

main_router.include_router(note_routes.router)
main_router.include_router(tag_routes.router)
main_router.include_router(file_routes.router)