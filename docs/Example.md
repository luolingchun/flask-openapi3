## Simple Demo

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

## REST Demo

```python
from http import HTTPStatus
from typing import Optional, List

from pydantic import BaseModel, Field

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_openapi3.models.security import HTTPBearer, OAuth2, OAuthFlows, OAuthFlowImplicit

info = Info(title='book API', version='1.0.0')
jwt = HTTPBearer(bearerFormat="JWT")
oauth2 = OAuth2(flows=OAuthFlows(
    implicit=OAuthFlowImplicit(
        authorizationUrl="https://example.com/api/oauth/dialog",
        scopes={
            "write:pets": "modify pets in your account",
            "read:pets": "read your pets"
        }
    )))
security_schemes = {"jwt": jwt, "oauth2": oauth2}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")


app = OpenAPI(__name__, info=info, security_schemes=security_schemes, responses={"404": NotFoundResponse})

book_tag = Tag(name='book', description='Some Book')
security = [
    {"jwt": []},
    {"oauth2": ["write:pets", "read:pets"]}
]

app.config["VALIDATE_RESPONSE"] = True


class BookPath(BaseModel):
    bid: int = Field(..., description='book id')


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description='Age')
    s_list: List[str] = Field(None, alias='s_list[]', description='some array')


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookBodyWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")
    data: Optional[BookBodyWithID]


@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    responses={"200": BookResponse},
    extra_responses={"200": {"content": {"text/csv": {"schema": {"type": "string"}}}}},
    security=security
)
def get_book(path: BookPath):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    if path.bid == 4:
        return NotFoundResponse().dict(), 404
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": 3, "author": 'no'}}


# set doc_ui False disable openapi UI
@app.get('/book', doc_ui=True, deprecated=True)
def get_books(query: BookQuery):
    """get books
    get all books
    """
    print(query)
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": 'a1'},
            {"bid": 2, "age": query.age, "author": 'a2'}
        ]
    }


@app.post('/book', tags=[book_tag], responses={"200": BookResponse})
def create_book(body: BookBody):
    print(body)
    return {"code": 0, "message": "ok"}, HTTPStatus.OK


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: BookPath, body: BookBody):
    print(path)
    print(body)
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag], doc_ui=False)
def delete_book(path: BookPath):
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
from flask_openapi3 import HTTPBearer
from flask_openapi3 import Tag, Info

info = Info(title='book API', version='1.0.0')
security_schemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

tag = Tag(name='book', description="Some Book")
security = [{"jwt": []}]


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


api = APIBlueprint(
    '/book',
    __name__,
    url_prefix='/api',
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    # disable openapi UI
    doc_ui=True
)


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class Path(BaseModel):
    bid: int = Field(..., description='book id')


@api.get('/book', doc_ui=False)
def get_book():
    return {"code": 0, "message": "ok"}


@api.post('/book', extra_responses={"200": {"content": {"text/csv": {"schema": {"type": "string"}}}}})
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put('/book/<int:bid>')
def update_book(path: Path, body: BookBody):
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


class UploadFileForm(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="File Type")


@app.post('/upload')
def upload_file(form: UploadFileForm):
    print(form.file.filename)
    print(form.file_type)
    form.file.save('test.jpg')
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
```

## A complete project

see [flask-api-demo](https://github.com/luolingchun/flask-api-demo)