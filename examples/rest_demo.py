# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:24
from typing import Optional

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag
from flask_openapi3.models.security import HTTPBearer

info = Info(title='book API', version='1.0.0')
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, securitySchemes=securitySchemes)

book_tag = Tag(name='book', description='Some Book')
security = [{"jwt": []}]


class Path(BaseModel):
    bid: int = Field(..., description='book id')


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookDataWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")
    data: BookDataWithID


@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: Path, query: BookData):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}, 522


@app.get('/book', tags=[book_tag])
def get_books(query: BookData):
    """get books
    get all books
    """
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": query.author},
            {"bid": 2, "age": query.age, "author": query.author}
        ]
    }


@app.post('/book', tags=[book_tag])
def create_book(body: BookData):
    print(body)
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: Path, body: BookData):
    print(path)
    print(body)
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag])
def delete_book(path: Path):
    print(path)
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
