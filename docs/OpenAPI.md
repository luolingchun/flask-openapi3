**`flask-openapi3`** provide [Swagger](https://swagger.io) and [ReDoc](https://redocly.github.io/redoc/) reference documentation. Before this, you should Learn something about OpenAPI [spec]([OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)). 

## Info

You must import **`Info`** from **`flask-openapi3.models.info`**, it needs some parameters: **`title`**, **`version`** ... , more information see the [OpenAPI Specification info-object](https://spec.openapis.org/oas/v3.0.3#info-object).

```python
from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info


info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)
api = APIBlueprint('/book', __name__, url_prefix='/api')


if __name__ == '__main__':
    app.run()
```

run it, and go to http://127.0.0.1:5000/openapi, you will see the reference documentation.

![image-20210525160157057](./assets/image-20210525160157057.png)

## Tag

You can also specify tag for apis, like this:

```python
...

book_tag = Tag(name='book', description='Book')


@api.get('/book', tags=[book_tag])
def get_book():


...
```

and then you will get the magic.

![image-20210525160744617](./assets/image-20210525160744617.png)

## securitySchemes

like [Info](#info), import **`HTTPBearer`** from **`flask-openapi3.models.flask_openapi3.models.security`**, more features see the [OpenAPI Specification security-scheme-object](https://spec.openapis.org/oas/v3.0.3#security-scheme-object).

First, you need define the **securitySchemes**  and **security** variable:

```python
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}
security = [{"jwt": []}]
```

Second, add pass the **security** to your api, like this:

```python
@api.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path, query: BookData):
    ...
```

result:

![image-20210525165350520](./assets/image-20210525165350520.png)

## Request validate

First, you need to import `BaseModel` from `pydantic`:

```python
from pydantic import BaseModel
```

### path

Request parameter in rules，**`@app.get('/book/<int:bid>')`**.

You have to declare path model as a class that inherits from  **`BaseModel`**:

```python
class Path(BaseModel):
    bid: int = Field(..., description='book id')
        
@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path):
    ...
```

### query

Receive flask **`resuqet.args`**.

like path, you need pass **`query`** to view function.

```python
class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')

@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path, query: BookData):
    ...
```

### form 

Receive flask **`resuqet.form`** and **`request.files`**.

```python
class UploadFile(BaseModel):
    file: FileStorage # request.files["file"]
    file_type: str = Field(None, description="File type")


@app.post('/upload')
def upload_file(form: UploadFile):
    ...
```

### body

Receive flask **`resuqet.json`**.

```python
class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')

@app.post('/book', tags=[book_tag])
def create_book(body: BookData):
    ...
```

### header

Receive flask **`resuqet.headers`**.

### cookies

Receive flask **`resuqet.cookies`**.

## Response validate

If you want to validate response and generate **Schemas**, pass the **`responses`**.

```python
class BookDataWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookResponse(BaseModel):
    code: int = Field(0, description="status code")
    message: str = Field("ok", description="exception information")
    data: BookDataWithID

@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: Path, query: BookData):
    """get book
    get book by id, age or author
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}
```

default :**`validate_resp=True`**, you can set **`validate_resp=False`** to only  generate **Schemas** in swagger-ui.

![image-20210526104627124](./assets/image-20210526104627124.png)

## OpenAPI spec

If you need the complete spec(json) , go to http://127.0.0.1:5000/openapi/openapi.json

