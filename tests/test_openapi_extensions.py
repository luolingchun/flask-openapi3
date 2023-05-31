# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/5/31 14:32
import pytest

from flask_openapi3 import OpenAPI, APIBlueprint, APIView

app = OpenAPI(__name__, openapi_extensions={
    "x-google-endpoints": [
        {
            "name": "my-cool-api.endpoints.my-project-id.cloud.goog",
            "allowCors": True
        }
    ]
})

openapi_extensions = {
    "x-google-backend": {
        "address": "https://<NODE_SERVICE_ID>-<HASH>.a.run.app",
        "protocol": "h2"
    }
}

app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get("/", openapi_extensions=openapi_extensions)
def hello():
    return "ok"


# APIBlueprint
api = APIBlueprint("book", __name__, url_prefix="/api")


@api.get('/book', openapi_extensions=openapi_extensions)
def get_book():
    return {"code": 0, "message": "ok"}


app.register_api(api)

# APIView
api_view = APIView()


@api_view.route("/view/book")
class BookListAPIView:

    @api_view.doc(openapi_extensions=openapi_extensions)
    def post(self):
        return "ok"


app.register_api_view(api_view)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json: dict = resp.json
    assert resp.status_code == 200
    assert _json.get("x-google-endpoints") is not None
    assert _json["paths"]["/"]["get"]["x-google-backend"] is not None
    assert _json["paths"]["/api/book"]["get"]["x-google-backend"] is not None
    assert _json["paths"]["/view/book"]["post"]["x-google-backend"] is not None
