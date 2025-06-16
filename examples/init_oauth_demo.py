# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/6/21 11:23
from flask_openapi3 import Info
from flask_openapi3 import OpenAPI

info = Info(title="oauth API", version="1.0.0")

# https://spec.openapis.org/oas/v3.1.0#implicit-oauth2-sample
oauth2 = {
    "type": "oauth2",
    "flows": {
        "implicit": {
            "authorizationUrl": "https://accounts.google1.com/o/oauth2/v2/auth",
            "tokenUrl": "https://www.googleapis1.com/oauth2/v4/token",
            "scopes": {
                "write:pets": "modify pets in your account",
                "read:pets": "read your pets"
            }
        }
    }
}
security_schemes = {"oauth2": oauth2}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

# https://github.com/swagger-api/swagger-ui/blob/0ce792c9d0965a8b6b5d75f5e1341ff6936a4cb0/docs/usage/oauth2.md
oauth_config = {
    "clientId": "xxx",
    "clientSecret": "xxx"
}
app.config["OAUTH_CONFIG"] = oauth_config

# https://spec.openapis.org/oas/v3.1.0#oauth2-security-requirement
security = [
    {"oauth2": ["write:pets", "read:pets"]}
]


@app.get("/", security=security)
def oauth():
    return "oauth"


if __name__ == '__main__':
    app.run(debug=True)
