First, you need to import `BaseModel` from `pydantic`:

```python
from pydantic import BaseModel
```

## Request parameter declaration

### path

Request parameter in rules，**`@app.get('/book/<int:bid>')`**.

You have to declare **path** model as a class that inherits from  **`BaseModel`**:

```python hl_lines="6"
class BookPath(BaseModel):
    bid: int = Field(..., description='book id')


@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: BookPath):
    ...
```

### query

Receive flask **`request.args`**.

!!! info

    ```python
    from flask import request
    ```

like [path](#path), you need pass **`query`** to view function.

```python hl_lines="7"
class BookQuery(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: BookPath, query: BookQuery):
    ...
```

### form

Receive flask **`request.form`** and **`request.files`**.

```python hl_lines="7"
class UploadFileForm(BaseModel):
    file: FileStorage  # request.files["file"]
    file_type: str = Field(None, description="File type")


@app.post('/upload')
def upload_file(form: UploadFileForm):
    ...
```

### body

Receive flask **`request.json`**.

```python hl_lines="7"
class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


@app.post('/book', tags=[book_tag])
def create_book(body: BookBody):
    ...
```

### header

Receive flask **`request.headers`**.

### cookie

Receive flask **`request.cookies`**.

## Operation fields

*new in v2.1.0*

### extra_form

Extra form information can be provided using `extra_form` as in the following sample:

```python hl_lines="8"
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

### extra_body

Extra body information can be provided using `extra_body` as in the following sample:

```python hl_lines="25"
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