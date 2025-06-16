# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/11 13:37

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
