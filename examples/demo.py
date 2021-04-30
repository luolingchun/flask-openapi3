# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:24

from flask import Flask
from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info

info = Info(title='test API', version='1.0.0')

app = Flask(__name__)
openapi = OpenAPI(info=info, app=app)


@app.route('/book', methods=['POST'])
def create_book():
    return ''


if __name__ == '__main__':
    # print(app.url_map)
    app.run(debug=True)
