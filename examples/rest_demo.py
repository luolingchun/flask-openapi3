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

book_tag = Tag(name='book', description='图书')
security = [{"jwt": []}]


class Path(BaseModel):
    bid: int = Field(..., description='图书id')


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='年龄')
    author: str = Field(None, min_length=2, max_length=4, description='作者')


class BookDataWithID(BaseModel):
    bid: int = Field(..., description='图书id')
    age: Optional[int] = Field(None, ge=2, le=4, description='年龄')
    author: str = Field(None, min_length=2, max_length=4, description='作者')


class BookResponse(BaseModel):
    code: int = Field(0, description="状态码")
    message: str = Field("ok", description="异常信息")
    data: BookDataWithID


@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: Path, query: BookData):
    """获取图书
    根据图书id获取图书
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
def create_book(json: BookData):
    print(json)
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: Path, json: BookData):
    print(path)
    print(json)
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag])
def delete_book(path: Path):
    print(path)
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
