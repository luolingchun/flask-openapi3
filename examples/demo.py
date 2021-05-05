# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:24
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag

info = Info(title='test API', version='1.0.0')

# app = Flask(__name__)
app = OpenAPI(__name__, info=info)


class Type(BaseModel):
    name: str


class Category(str, Enum):
    """图书类别枚举"""
    c1 = '1'
    c2 = '2'


class Path(BaseModel):
    bid: int = Field(..., description='图书id')
    ttt: str = Field(None, description="ttttt")


class Query(BaseModel):
    age: Optional[int] = Field(None, ge=2, le=4, description='年龄')
    author: str = Field(None, min_length=2, max_length=4, description='作者')
    category: Category = Field(None, description="图书类别")


book_tag = Tag(name='book', description='图书')


@app.get('/book/<string:ttt>/<int:bid>', tags=[book_tag])
def get_book(path: Path, query: Query):
    """获取图书
    根据图书id获取图书
    """
    print(path.bid)
    print(path.ttt)
    print(query)
    return {"bid": path.bid}


if __name__ == '__main__':
    # print(app.url_map)
    app.run(debug=True)
