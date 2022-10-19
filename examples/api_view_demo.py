# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/10/18 9:00
from flask.views import MethodView

from flask_openapi3 import OpenAPI
from flask_openapi3.view import APIView

app = OpenAPI(__name__)

api_view = APIView()


@api_view.route("/book")
class BookView:
    # @api_view.doc(summary="获取")
    def get(self):
        return "ok"

    # @api_view.doc(summary="新建")
    def post(self):
        return "ok1"


app.register_api_view(api_view)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
