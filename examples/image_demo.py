# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/6/26 17:05

from flask import make_response

from flask_openapi3 import OpenAPI


app = OpenAPI(__name__)


@app.get("/image")
def get_image():
    with open("../docs/images/openapi.png", "rb") as f:
        content = f.read()

    response = make_response(content)
    response.mimetype = "image/png"
    return response


if __name__ == "__main__":
    app.run(debug=True)
