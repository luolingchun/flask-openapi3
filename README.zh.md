# flask-openapi3

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/luolingchun/flask-openapi3/test)](https://github.com/luolingchun/flask-openapi3/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/flask-openapi3)](https://pypi.org/project/flask-openapi3/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-openapi3)](https://pypistats.org/packages/flask-openapi3)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-openapi3)](https://pypi.org/project/flask-openapi3/)

为你的 Flask 项目生成 RESTful API 和 OpenAPI 文档。

## 依赖

Python =3.7+

flask-openapi3 依赖以下库：

- [Flask](https://github.com/pallets/flask)：用于WEB服务
- [Pydantic](https://github.com/samuelcolvin/pydantic)：用于数据验证

## 安装

```bash
pip install -U flask-openapi3
```

## 一个简单的示例

这里有一个简单的示例，更多示例请查看[示例](https://luolingchun.github.io/flask-openapi3/zh/Example/)。

```python
from pydantic import BaseModel

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)

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
```

## API 文档

运行[简单示例](https://github.com/luolingchun/flask-openapi3/blob/master/examples/simple_demo.py)，然后访问 http://127.0.0.1:5000/openapi。

你将看到文档入口：[Swagger UI](https://github.com/swagger-api/swagger-ui) 和 [Redoc](https://github.com/Redocly/redoc)。

![openapi](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi.png)
![openapi-swagger](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-swagger.png)
![openapi-redoc](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-redoc.png)

