# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/12/9 17:50

import orjson
from flask.json.provider import JSONProvider

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI


class OrJSONProvider(JSONProvider):
    # https://github.com/ijl/orjson#option
    option = orjson.OPT_INDENT_2

    def dumps(self, obj, **kwargs):
        return orjson.dumps(obj, option=self.option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)


info = Info(title='book API', version='1.0.0')
app = OpenAPI(__name__, info=info)
# use orjson
orjson_provider = OrJSONProvider(app)
app.json = orjson_provider


@app.get('/book')
def get_book():
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": 18, "author": "tom"},
            {"bid": 2, "age": 19, "author": "alice"},
            {"bid": 3, "age": 20, "author": "中文测试"}
        ]
    }


if __name__ == '__main__':
    app.run(debug=True)
