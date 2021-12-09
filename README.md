# flask-openapi3

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/luolingchun/flask-openapi3/test)](https://github.com/luolingchun/flask-openapi3/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/flask-openapi3)](https://pypi.org/project/flask-openapi3/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-openapi3)](https://pypistats.org/packages/flask-openapi3)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-openapi3)](https://pypi.org/project/flask-openapi3/)

Generate RESTful API and OpenAPI document for your Flask project.

## Requirements

Python 3.7+

flask-openapi3 be dependent on the following libraries:

- [Flask](https://github.com/pallets/flask) for the web app.
- [Pydantic](https://github.com/samuelcolvin/pydantic) for the data validation.

## Installation

```bash
pip install -U flask-openapi3
```

## A Simple Example

Here's a simple example, further go to the [Example](https://luolingchun.github.io/flask-openapi3/en/Example/).

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

## API docs

Run the [simple example](https://github.com/luolingchun/flask-openapi3/blob/master/examples/simple_demo.py), and go
to http://127.0.0.1:5000/openapi.

You will see the document: [Swagger UI](https://github.com/swagger-api/swagger-ui)
and [Redoc](https://github.com/Redocly/redoc).

![openapi](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi.png)
![openapi-swagger](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-swagger.png)
![openapi-redoc](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-redoc.png)

