## responses

If you want to generate **Schemas**, pass the **`responses`**.

```python hl_lines="13"
class BookBodyWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookResponse(BaseModel):
    code: int = Field(0, description="status code")
    message: str = Field("ok", description="exception information")
    data: BookBodyWithID


@app.get('/book/<int:bid>', 
         tags=[book_tag], 
         responses={
             "200": BookResponse, 
             # Version 2.4.0 starts supporting response for dictionary types
             "201": {"content": {"text/csv": {"schema": {"type": "string"}}}}
         })
def get_book(path: BookPath, query: BookBody):
    """get a book
    get book by id, age or author
    """
    return {"code": 0, "message": "ok", "data": {}}
```

*New in v2.5.0*

Now you can use `string`, `int`, and `HTTPStatus` as response's key.

```python hl_lines="5 7"
from http import HTTPStatus


class BookResponse(BaseModel):
    message: str = Field(..., description="The message")

    
@api.get("/hello/<string:name>",
        responses={
            HTTPStatus.OK: BookResponse, 
            "201": {"content": {"text/csv": {"schema": {"type": "string"}}}},
            204: None
        })
def hello(path: HelloPath):
    message = {"message": f"""Hello {path.name}!"""}

    response = make_response(json.dumps(message), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response
```


![image-20210526104627124](../assets/image-20210526104627124.png)

## extra_responses

*New in v2.4.0*

!!! Deprecated-Warning warning

    `extra_responses` have been merged into the `responses`, and `extra_responses` will be deprecated in v3.x.

*New in v1.0.0*

You can pass to your path operation decorators a parameter `extra_responses`.

It receives a `dict`, the keys are status codes for each response, like `200`, and the values are other dicts with the
information for each of them.

Like this:

```python
@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    responses={"200": BookResponse},
    extra_responses={"201": {"content": {"text/csv": {"schema": {"type": "string"}}}}},
    security=security
)
def get_book(path: BookPath):
    ...


@api.post('/book', extra_responses={"201": {"content": {"text/csv": {"schema": {"type": "string"}}}}})
def create_book(body: BookBody):
    ...
```

## More information about OpenAPI responses

- [OpenAPI Responses Object](https://spec.openapis.org/oas/v3.0.3#responses-object), it includes the Response Object.
- [OpenAPI Response Object](https://spec.openapis.org/oas/v3.0.3#response-object).

