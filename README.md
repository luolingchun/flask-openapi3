<div align="center">
    <a href="https://luolingchun.github.io/flask-openapi3/" target="_blank">
        <img class="off-glb" src="https://raw.githubusercontent.com/luolingchun/flask-openapi3/master/docs/images/logo-text.svg" 
             width="60%" height="auto" alt="logo">
    </a>
</div>
<p align="center">
    <em>Generate REST API and OpenAPI documentation for your Flask project.</em>
</p>
<p align="center">
    <a href="https://github.com/luolingchun/flask-openapi3/actions/workflows/tests.yml" target="_blank">
        <img class="off-glb" src="https://img.shields.io/github/actions/workflow/status/luolingchun/flask-openapi3/tests.yml?branch=master" alt="test">
    </a>
    <a href="https://pypi.org/project/flask-openapi3/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/v/flask-openapi3" alt="pypi">
    </a>
    <a href="https://pypistats.org/packages/flask-openapi3" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/dm/flask-openapi3" alt="pypistats">
    </a>
    <a href="https://pypi.org/project/flask-openapi3/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/pyversions/flask-openapi3" alt="pypi versions">
    </a>
</p>

**Flask OpenAPI3** is a web API framework based on **Flask**. It uses **Pydantic** to verify data and automatic
generation of interaction documentation: **Swagger**, **ReDoc** and **RapiDoc**.

The key features are:

- **Easy to code:** Easy to use and easy to learn

- **Standard document specification:** Based on [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)

- **Interactive OpenAPI documentation:** [Swagger](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc) and [RapiDoc](https://github.com/rapi-doc/RapiDoc)
  
- **Data validation:** Fast data verification based on [Pydantic](https://github.com/pydantic/pydantic)

- **Authorization:** Support to reload authorizations in Swagger UI

## Requirements

Python 3.8+

flask-openapi3 is dependent on the following libraries:

- [Flask](https://github.com/pallets/flask) for the web app.
- [Pydantic](https://github.com/pydantic/pydantic) for the data validation.

## Installation

```bash
pip install -U flask-openapi3
```

or

```bash
conda install -c conda-forge flask-openapi3
```

<details markdown="block">
<summary>Optional dependencies</summary>

- [python-email-validator](https://github.com/JoshData/python-email-validator) supports email verification.
- [python-dotenv](https://github.com/theskumar/python-dotenv#readme) enables support for [Environment Variables From dotenv](https://flask.palletsprojects.com/en/latest/cli/#dotenv) when running `flask` commands.
- [pyyaml](https://github.com/yaml/pyyaml) is used to output the OpenAPI document in yaml format.
- [asgiref](https://github.com/django/asgiref) allows views to be defined with `async def` and use `await`.

To install these dependencies with flask-openapi3:

```bash
pip install flask-openapi3[yaml]
# or
pip install flask-openapi3[async]
# or
pip install flask-openapi3[dotenv]
# or
pip install flask-openapi3[email]
# or all
pip install flask-openapi3[yaml,async,dotenv,email]
# or manually
pip install pyyaml asgiref python-dotenv email-validator
```
</details>

## A Simple Example

Here's a simple example, further go to the [Example](https://luolingchun.github.io/flask-openapi3/latest/Example/).

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


@app.get("/book", summary="get books", tags=[book_tag])
def get_book(query: BookQuery):
    """
    to get all books
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

<details>
<summary>Class-based API View Example</summary>

```python
from typing import Optional

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, Tag, Info, APIView


info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)

api_view = APIView(url_prefix="/api/v1", view_tags=[Tag(name="book")])


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description='Age')


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


@api_view.route("/book")
class BookListAPIView:
    a = 1

    @api_view.doc(summary="get book list")
    def get(self, query: BookQuery):
        print(self.a)
        return query.model_dump_json()

    @api_view.doc(summary="create book")
    def post(self, body: BookBody):
        """description for a created book"""
        return body.model_dump_json()


@api_view.route("/book/<id>")
class BookAPIView:
    @api_view.doc(summary="get book")
    def get(self, path: BookPath):
        print(path)
        return "get"

    @api_view.doc(summary="update book")
    def put(self, path: BookPath):
        print(path)
        return "put"

    @api_view.doc(summary="delete book", deprecated=True)
    def delete(self, path: BookPath):
        print(path)
        return "delete"


app.register_api_view(api_view)

if __name__ == "__main__":
    app.run(debug=True)
```
</details>

## API Document

Run the [simple example](https://github.com/luolingchun/flask-openapi3/blob/master/examples/simple_demo.py), and go to http://127.0.0.1:5000/openapi.

You will see the documentation: [Swagger](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc) and [RapiDoc](https://github.com/rapi-doc/RapiDoc).

![openapi](https://raw.githubusercontent.com/luolingchun/flask-openapi3/master/docs/images/openapi.png)
![openapi-swagger](https://raw.githubusercontent.com/luolingchun/flask-openapi3/master/docs/images/openapi-swagger.png)
![openapi-redoc](https://raw.githubusercontent.com/luolingchun/flask-openapi3/master/docs/images/openapi-redoc.png)
![openapi-RapiDoc](https://raw.githubusercontent.com/luolingchun/flask-openapi3/master/docs/images/openapi-rapidoc.png)
