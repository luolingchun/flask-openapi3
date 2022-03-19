Like [Info](/flask-openapi3/en/OpenAPI/Info/), import **`HTTPBearer`** from **`flask_openapi3`**, more features see
the [OpenAPI Specification Security Scheme Object](https://spec.openapis.org/oas/v3.0.3#security-scheme-object).

First, you need define the **security_schemes**  and **security** variable:

```python
security_schemes = {"jwt": HTTPBearer(bearerFormat="JWT")}
security = [{"jwt": []}]

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
```

Second, add pass the **security** to your api, like this:

```python hl_lines="1"
@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path, query: BookBody):
    ...
```

result:

![image-20210525165350520](../assets/image-20210525165350520.png)

### abp_security

*New in v0.9.3*

You don't need to specify **security** for every api.

```python hl_lines="3"
tag = Tag(name='book', description="Some Book")
security = [{"jwt": []}]
api = APIBlueprint('/book', __name__, abp_tags=[tag], abp_security=security)


@api.post('/book')
def create_book(body: BookBody):
    ...
```
