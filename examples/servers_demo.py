# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/1/8 14:25
from pydantic import BaseModel

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI, Server

info = Info(title='book API', version='1.0.0')
servers = [
    Server(url='http://127.0.0.1:5000'),
    Server(url='https://127.0.0.1:5000'),
]
app = OpenAPI(__name__, info=info, servers=servers)

book_tag = Tag(name='book', description='Some Book')


class BookQuery(BaseModel):
    age: int
    author: str


@app.get('/book', tags=[book_tag])
def get_book(query: BookQuery):
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


if __name__ == '__main__':
    app.run(debug=True)
