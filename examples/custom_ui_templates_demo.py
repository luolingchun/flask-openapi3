# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/2/3 15:14
from pydantic import BaseModel

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title="book API", version="1.0.0")
swagger_html_string = """
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
"""

rapipdf_html_string = """
<!doctype html>
  <html>
  <head>
    <script src="https://unpkg.com/rapipdf/dist/rapipdf-min.js"></script>
  </head>
  <body>
    <rapi-pdf
      style = "width:700px; height:40px; font-size:18px;"
      spec-url = "{{api_doc_url}}"
      button-bg = "#b44646"
    > </rapi-pdf>
  </body>
  </html>
"""
ui_templates = {
    "swagger": swagger_html_string,
    "rapipdf": rapipdf_html_string
}
app = OpenAPI(__name__, info=info, ui_templates=ui_templates)

book_tag = Tag(name='book', description='Some Book')


class BookQuery(BaseModel):
    age: int
    author: str


@app.get('/book', tags=[book_tag])
def get_book(query: BookQuery):
    """get books
    to get all books
    """
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": query.author},
            {"bid": 2, "age": query.age, "author": query.author}
        ]
    }


if __name__ == '__main__':
    app.run(debug=True)
