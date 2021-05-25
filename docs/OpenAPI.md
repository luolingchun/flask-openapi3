**`flask-openapi3`** provide [Swagger](https://swagger.io) and [ReDoc](https://redocly.github.io/redoc/) reference documentation. Before this, you should Learn something about OpenAPI [spec]([OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)). 

## Info

You must import **`Info`** from **`flask-openapi3.models.info`**, it needs some paramters: **`title`**, **`version`** ... , more information see the [OpenAPI Specification info-object](https://spec.openapis.org/oas/v3.0.3#info-object).

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

book_tag = Tag(name='book', description='图书')


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

todo:

- validate
- openapi.json