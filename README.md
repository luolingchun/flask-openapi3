<div align="center">
    <a href="https://luolingchun.github.io/flask-openapi3/" target="_blank">
        <img src="https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/logo-text.png" width="50%"
             height="auto" alt="logo">
    </a>
</div>
<p align="center">
    <em>Generate REST API and OpenAPI documentation for your Flask project.</em>
</p>
<p align="center">
    <a href="https://github.com/luolingchun/flask-openapi3/actions/workflows/test.yml" target="_blank">
        <img src="https://img.shields.io/github/workflow/status/luolingchun/flask-openapi3/test" alt="test">
    </a>
    <a href="https://pypi.org/project/flask-openapi3/" target="_blank">
        <img src="https://img.shields.io/pypi/v/flask-openapi3" alt="pypi">
    </a>
    <a href="https://pypistats.org/packages/flask-openapi3" target="_blank">
        <img src="https://img.shields.io/pypi/dm/flask-openapi3" alt="pypistats">
    </a>
    <a href="https://pypi.org/project/flask-openapi3/" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/flask-openapi3" alt="pypi versions">
    </a>
</p>

**Flask OpenAPI3** is a web API framework based on **Flask**. It uses **Pydantic** to verify data and automatic
generation of interaction documentation: **Swagger**, **ReDoc** and **RapiDoc**.

The key features are:

- **Easy to code:** Easy to use and easy to learn

- **Standard document specification:** Based on [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification)

- **Interactive OpenAPI documentation:** [Swagger](https://github.com/swagger-api/swagger-ui), 
  [Redoc](https://github.com/Redocly/redoc) and [RapiDoc](https://github.com/mrin9/RapiDoc)

- **Data validation:** Fast data verification based on [Pydantic](https://github.com/samuelcolvin/pydantic)

- **Authorization:** Support to reload authorizations in Swagger UI

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

info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)

book_tag = Tag(name="book", description="Some Book")


class BookQuery(BaseModel):
    age: int
    author: str


@app.get("/book", tags=[book_tag])
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


if __name__ == "__main__":
    app.run(debug=True)
```

## API Document

Run the [simple example](https://github.com/luolingchun/flask-openapi3/blob/master/examples/simple_demo.py), and go
to http://127.0.0.1:5000/openapi.

You will see the documentation: [Swagger](https://github.com/swagger-api/swagger-ui), 
[Redoc](https://github.com/Redocly/redoc) and [RapiDoc](https://github.com/mrin9/RapiDoc).

![openapi](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi.png)
![openapi-swagger](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-swagger.png)
![openapi-redoc](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-redoc.png)
![openapi-RapiDoc](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi-rapidoc.png)
