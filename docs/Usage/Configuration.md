Flask supports many [configurations](https://flask.palletsprojects.com/en/latest/config/), and there are also some
configurations in this library that can be used.

## SWAGGER_HTML_STRING

You can customize the custom behavior of this template.

[The default `SWAGGER_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-swagger/flask_openapi3_swagger/templates/__init__.py).

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

[More configuration options for Swagger UI](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).

## OAUTH_CONFIG

You can configure OAuth 2.0 authorization for Swagger UI.

```python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

app.config["OAUTH_CONFIG"] = {"clientId": "xxx", "clientSecret": "xxx"}
```

[More configuration options for Swagger UI](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md).

## SCALAR_HTML_STRING

You can customize the custom behavior of this template.

[The default `SCALAR_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-scalar/flask_openapi3_scalar/templates/__init__.py).

## SCALAR_CONFIG

You can change the default behavior of the Scalar UI.

[More configuration options for Swagger UI](https://github.com/scalar/scalar/blob/main/documentation/configuration.md).

## REDOC_HTML_STRING
You can customize the custom behavior of this template.

[The default `REDOC_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-redoc/flask_openapi3_redoc/templates/__init__.py).

## REDOC_CONFIG

You can change the default behavior of the Redoc UI.

[More configuration options for Redoc UI](https://github.com/Redocly/redoc/blob/main/docs/config.md).

## RAPIDOC_HTML_STRING

You can customize the custom behavior of this template.

[The default `RAPIDOC_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-rapidoc/flask_openapi3_rapidoc/templates/__init__.py).

## RAPIDOC_CONFIG

You can change the default behavior of the Rapidoc UI.

[More configuration options for Rapidoc UI](https://rapidocweb.com/examples.html).

## RAPIPDF_HTML_STRING

You can customize the custom behavior of this template.

[The default `RAPIPDF_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-rapipdf/flask_openapi3_rapipdf/templates/__init__.py).

## RAPIPDF_CONFIG

You can change the default behavior of the Rapipdf UI.

[More configuration options for Rapipdf UI](https://mrin9.github.io/RapiPdf/).

## ELEMENTS_HTML_STRING

You can customize the custom behavior of this template.

[The default `ELEMENTS_HTML_STRING` is here](https://github.com/luolingchun/flask-openapi3-plugins/blob/master/flask-openapi3-elements/flask_openapi3_elements/templates/__init__.py).


## ELEMENTS_CONFIG

You can change the default behavior of the Elements UI.

[More configuration options for Rapipdf UI](https://github.com/stoplightio/elements/blob/main/docs/getting-started/elements/elements-options.md).