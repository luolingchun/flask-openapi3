Flask supports many [configurations](https://flask.palletsprojects.com/en/latest/config/), and there are also some
configurations in this library that can be used.

## SWAGGER_CONFIG

You can change the default behavior of the Swagger UI.

```python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

app.config["SWAGGER_CONFIG"] = {
    "docExpansion": "none",
    "validatorUrl": "https://www.b.com"
}
```

Here are more configuration options for Swagger UI, which you can
find [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).

## OAUTH_CONFIG

You can configure OAuth 2.0 authorization for Swagger UI.

```python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

app.config["OAUTH_CONFIG"] = {"clientId": "xxx", "clientSecret": "xxx"}
```

Here are more configuration options for OAuth 2.0 configuration, which you can
find [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md).