from math import ceil
from enum import Enum
from typing import Annotated, Generic, TypeVar

from fastapi import Request
from pydantic import BaseModel, Field, AnyHttpUrl

SchemaType = TypeVar("SchemaType")


class OrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PageParams(BaseModel):
    page: int = Field(ge=1, le=1000000000, default=1) # this le is optional, so it is limit not to exceed postgres limits
    size: int = Field(ge=1, le=100, default=100) # page - offset, size - limit
    order: OrderEnum


class Metadata(BaseModel):
    page: int # current page number
    size: int # size number of results per page
    pages: int # total number of pages
    total: int # total number of results
    order: OrderEnum


class Links(BaseModel):
    self: AnyHttpUrl # link to current page
    next: AnyHttpUrl | None # link to next page
    prev: AnyHttpUrl | None # link to previous page
    first: AnyHttpUrl # link to first page
    last: AnyHttpUrl # link to last page


class Page(BaseModel, Generic[SchemaType]):
    metadata: Metadata
    links: Links
    results: list[SchemaType]


def paginate(pagination_params: PageParams, total: int, results: list[SchemaType], request: Request) -> Page[SchemaType]:
    url = request.url
    page = pagination_params.page
    size = pagination_params.size
    pages = ceil(total / pagination_params.size)
    order = pagination_params.order
    metadata = Metadata(
        page=page,
        size=size,
        pages=pages,
        total=total,
        order=order,
    )
    links = Links(
        self=str(url),
        next=str(url.include_query_params(page=page + 1)) if page * size < total else None,
        prev=str(url.include_query_params(page=page - 1)) if pagination_params.page - 1 >= 1 else None,
        first=str(url.include_query_params(page=1)),
        last=str(url.include_query_params(page=ceil(total / pagination_params.size) if total > 0 and pagination_params.size > 0 else 1)),
    )
    pagination_reports = Page(
        metadata=metadata,
        links=links,
        results=results,
    )
    return pagination_reports
