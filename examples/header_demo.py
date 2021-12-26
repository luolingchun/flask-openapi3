# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/26 15:07

from pydantic import BaseModel, Field

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title='header API', version='1.0.0')
app = OpenAPI(__name__, info=info)

book_tag = Tag(name='book', description='Some Book')


class Headers(BaseModel):
    hello: str = Field("what's up", max_length=12, description='sds')
    # required
    # hello: str = Field(..., max_length=12, description='sds')


@app.get('/book', tags=[book_tag])
def get_book(header: Headers):
    print(header)
    return header.hello


if __name__ == '__main__':
    app.run(debug=True)
