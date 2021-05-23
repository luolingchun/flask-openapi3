# flask-openapi3

Generate RESTful API and OpenAPI document for your Flask project.

## Installation

```bash
$ pip install -U flask-openapi3
```

## A Simple Example

```python
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
```

## API docs

Run the [simple example](https://github.com/luolingchun/flask-openapi3/blob/master/examples/simple_demo.py), and go to http://127.0.0.1:5000/openapi.

You will see the document: [Swagger UI](https://github.com/swagger-api/swagger-ui) and [Redoc](https://github.com/Redocly/redoc).

![openapi](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi.png)
![openapi-swagger](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-swagger.png)
![openapi-redoc](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-redoc.png)

