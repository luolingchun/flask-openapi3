## Simple Demo

```python
from pydantic import BaseModel

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag

info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)

book_tag = Tag(name='book', description='Some Book')


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

## REST Demo

```python
from typing import Optional

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag
from flask_openapi3.models.security import HTTPBearer

info = Info(title='book API', version='1.0.0')
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, securitySchemes=securitySchemes)

book_tag = Tag(name='book', description='Some Book')
security = [{"jwt": []}]


class Path(BaseModel):
    bid: int = Field(..., description='book id')


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookDataWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Message")
    data: BookDataWithID


@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: Path, query: BookData):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
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
def create_book(body: BookData):
    print(body)
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: Path, body: BookData):
    print(path)
    print(body)
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag])
def delete_book(path: Path):
    print(path)
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
```

## APIBlueprint

```python
from typing import Optional

from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, OpenAPI
from flask_openapi3.models import Tag, Info

info = Info(title='book API', version='1.0.0')
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, securitySchemes=securitySchemes)

tag = Tag(name='book', description="Some Book")
security = [{"jwt": []}]
api = APIBlueprint('/book', __name__, url_prefix='/api', abp_tags=[tag], abp_security=security)


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class Path(BaseModel):
    bid: int = Field(..., description='book id')


@api.post('/book')
def create_book(body: BookData):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>')
def update_book(path: Path, body: BookData):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


# register api
app.register_api(api)

if __name__ == '__main__':
    app.run(debug=True)
```

## Upload File Demo

```python
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, FileStorage

app = OpenAPI(__name__)


class UploadFile(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="File Type")


@app.post('/upload')
def upload_file(form: UploadFile):
    print(form.file.filename)
    print(form.file_type)
    form.file.save('test.jpg')
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
```

## A complete project

see [flask-api-demo](https://github.com/luolingchun/flask-api-demo)