## tag

You can also specify tag for apis like this:

```python hl_lines="3 6"
from flask_openapi3 import Tag

book_tag = Tag(name='book', description='Some Book')


@api.get('/book', tags=[book_tag])
def get_book():
    ...
```

and then you will get the magic.

![image-20210525160744617](../assets/image-20210525160744617.png)

### abp_tags

*New in v0.9.3*

You don't need to specify **tag** for every api.

```python hl_lines="3"
tag = Tag(name='book', description="Some Book")

api = APIBlueprint('/book', __name__, url_prefix='/api', abp_tags=[tag])


@api.post('/book')
def create_book(body: BookBody):
    ...
```

## summary and description

You need to add docs to the view-func. The first line is the **summary**, and the rest is the **description**. Like this:

```python hl_lines="3 4 5 6"
@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}
```

![image-20210605115557426](../assets/image-20210605115557426.png)

*New in v1.0.0*

Now keyword parameters `summary` and `description` is supported, it will be take first.

```python hl_lines="1"
@app.get('/book/<int:bid>', summary="new summary", description='new description')
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {}}
```

![Snipaste_2022-03-19_15-10-06.png](../assets/Snipaste_2022-03-19_15-10-06.png)

## external_docs

Allows referencing an external resource for extended documentation.

More information to see [External Documentation Object](https://spec.openapis.org/oas/v3.0.3#external-documentation-object).

```python hl_lines="10"
from flask_openapi3 import OpenAPI, ExternalDocumentation

app = OpenAPI(__name__, info=info)

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    external_docs=ExternalDocumentation(
        url="https://www.openapis.org/",
        description="Something great got better, get excited!")
)
def get_book(path: BookPath):
    ...
```

## operation_id

You can set `operation_id` for an api (operation). The default is automatically.

```python hl_lines="6"
@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    operation_id="get_book_id"
)
def get_book(path: BookPath):
    ...
```

## extra_form

*new in v2.1.0*

Extra form information can be provided using `extra_form` as in the following sample:

```python hl_lines="8"
from flask_openapi3 import ExtraRequestBody

extra_form = ExtraRequestBody(
    description="This is form RequestBody",
    required=True,
    # replace style (default to form)
    encoding={"str_list": Encoding(style="simple")}
)

@app.post('/book', extra_form=extra_form)
def create_book(body: BookForm):
    ...
```

## extra_body

*new in v2.1.0*

Extra body information can be provided using `extra_body` as in the following sample:

```python hl_lines="25"
from flask_openapi3 import ExtraRequestBody

extra_body = ExtraRequestBody(
    description="This is post RequestBody",
    required=True,
    example="ttt",
    examples={
        "example1": Example(
            summary="example summary1",
            description="example description1",
            value={
                "age": 24,
                "author": "author1"
            }
        ),
        "example2": Example(
            summary="example summary2",
            description="example description2",
            value={
                "age": 48,
                "author": "author2"
            }
        )
    }
)

@app.post('/book', extra_body=extra_body)
def create_book(body: BookForm):
    ...
```

## deprecated

*New in v1.0.0*

`deprecated`: mark as deprecated support. default to not True.

```python
@app.get('/book', deprecated=True)
def get_books(query: BookQuery):
    ...
```

## security

pass the **security** to your api, like this:

```python hl_lines="1"
@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path, query: BookBody):
    ...
```

There are many kinds of security supported here:

```python
basic = HTTPBase()
jwt = HTTPBearer()
api_key = APIKey(name='api key')
oauth2 = OAuth2(flows=OAuthFlows(
    implicit=OAuthFlowImplicit(
        authorizationUrl="https://example.com/api/oauth/dialog",
        scopes={
            "write:pets": "modify pets in your account",
            "read:pets": "read your pets"
        }
    )))
security_schemes = {"jwt": jwt, "api_key": api_key, "oauth2": oauth2, "basic": basic}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

security = [
    {"jwt": []},
    {"oauth2": ["write:pets", "read:pets"]},
    {"basic": []}
]

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    security=security
)
def get_book(path: BookPath):
    ...
```

## servers

An array of Server Objects, which provide connectivity information to a target server. If the server's property is not provided, or is an empty array, the default value would be a Server Object with an url value of /.

```python
from flask_openapi3 import OpenAPI, Server

app = OpenAPI(__name__, info=info)

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    servers=[Server(url="https://www.openapis.org/", description="openapi")]
)
def get_book(path: BookPath):
    ...
```

## doc_ui

You can pass `doc_ui=False` to disable the `OpenAPI spec` when init `OpenAPI `.

```python
app = OpenAPI(__name__, info=info, doc_ui=False)
```

*New in v0.9.4*

You can also use `doc_ui` in endpoint or when initializing `APIBlueprint`.

```python hl_lines="4 9"
api = APIBlueprint(
    '/book',
    __name__,
    doc_ui=False
)

# or

@api.get('/book', doc_ui=False)
def get_book():
    ...
```
