# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/10 17:01
from pydantic import BaseModel

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag

info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)

book_tag = Tag(name='book', description='图书')


class BookData(BaseModel):
    age: int
    author: str


@app.get('/book', tags=[book_tag])
def get_book(query: BookData):
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
