Flask OpenAPI3 supports [Swagger](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc)
and [RapiDoc](https://github.com/rapi-doc/RapiDoc) templates by default.

*New in v2.3.0*

You can customize templates use `ui_templates` in initializing OpenAPI.

```python
ui_templates = {
    "swagger": swagger_html_string,
    "rapipdf": rapipdf_html_string
}

app = OpenAPI(__name__, info=info, ui_templates=ui_templates)
```

In the above example, `swagger` will overwrite the original template and `rapipdf` is a new template.

You can do anything with `swagger_html_string`, `rapipdf_html_string` or `any_html_string`.

!!! info

    `api_doc_url` is a necessary parameter for rendering template, so you must define it in your template.

**swagger_html_string:**

```html hl_lines="5 32"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Custom Title</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }

        *, *:before, *:after {
            box-sizing: inherit;
        }

        body {
            margin: 0;
            background: #fafafa;
        }
    </style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-standalone-preset.js"></script>
<script>
    window.onload = function () {
        // Begin Swagger UI call region
        window.ui = SwaggerUIBundle({
            url: "{{api_doc_url}}",
            dom_id: "#swagger-ui",
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
        })
    }
</script>
</body>
</html>
```

**rapipdf_html_string:**

This will generate a new route, http://127.0.0.1:5000/openapi/rapipdf.

```html  hl_lines="9"
<!doctype html>
<html>
<head>
    <script src="https://unpkg.com/rapipdf/dist/rapipdf-min.js"></script>
</head>
<body>
<rapi-pdf
        style="width:700px; height:40px; font-size:18px;"
        spec-url="{{api_doc_url}}"
        button-bg="#b44646"
></rapi-pdf>
</body>
</html>
```
