First, you need to import `BaseModel` from `pydantic`:

```python
from pydantic import BaseModel
```

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