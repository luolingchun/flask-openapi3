# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/5/31 14:24
from flask_openapi3 import OpenAPI

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
    },
    "x-aperture-labs-portal": "blue"
}


@app.get("/", openapi_extensions=openapi_extensions)
def hello():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
