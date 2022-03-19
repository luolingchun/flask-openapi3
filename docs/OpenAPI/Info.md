**`flask-openapi3`** provide [Swagger UI](https://github.com/swagger-api/swagger-ui),
[Redoc](https://github.com/Redocly/redoc) and [RapiDoc](https://github.com/mrin9/RapiDoc) interactive documentation.
Before that, you should know something about the [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3).

You must import **`Info`** from **`flask-openapi3`**, it needs some parameters: **`title`**, **`version`**
... , more information see the [OpenAPI Specification Info Object](https://spec.openapis.org/oas/v3.0.3#info-object).

```python hl_lines="4 5"
from flask_openapi3 import Info
from flask_openapi3 import OpenAPI, APIBlueprint

info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)
api = APIBlueprint('/book', __name__, url_prefix='/api')

if __name__ == '__main__':
    app.run()
```

run it, and go to http://127.0.0.1:5000/openapi, you will see the documentation.

![openapi](https://github.com/luolingchun/flask-openapi3/raw/master/docs/images/openapi.png)
![image-20210525160157057](../assets/image-20210525160157057.png)