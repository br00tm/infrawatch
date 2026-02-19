"""Pagination utilities."""

from typing import List, TypeVar

from app.schemas.common import PaginatedResponse

T = TypeVar("T")


def paginate(
    items: List[T],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse[T]:
    """Create a paginated response."""
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def calculate_skip(page: int, page_size: int) -> int:
    """Calculate skip value for pagination."""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate total pages."""
    return (total + page_size - 1) // page_size if page_size > 0 else 0
