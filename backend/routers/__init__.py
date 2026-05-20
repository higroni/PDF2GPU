"""
API Routers modul.
"""

from .collections import router as collections_router
from .pdfs import router as pdfs_router
from .search import router as search_router

__all__ = [
    'collections_router',
    'pdfs_router',
    'search_router'
]

# Made with Bob
