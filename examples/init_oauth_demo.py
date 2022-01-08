# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/6/21 11:23
from flask_openapi3 import OpenAPI, OAuthConfig
from flask_openapi3 import Info
from flask_openapi3.models.security import OAuth2, OAuthFlows, OAuthFlowImplicit

info = Info(title='oauth API', version='1.0.0')

oauth_config = OAuthConfig(
    clientId="xxx",
    clientSecret="xxx"
)

oauth2 = OAuth2(flows=OAuthFlows(
    implicit=OAuthFlowImplicit(
        authorizationUrl="https://example.com/api/oauth/dialog",
        scopes={
            "write:pets": "modify pets in your account",
            "read:pets": "read your pets"
        }
    )))
security_schemes = {"oauth2": oauth2}

app = OpenAPI(__name__, info=info, oauth_config=oauth_config, security_schemes=security_schemes)

security = [
    {"oauth2": ["write:pets", "read:pets"]}
]


@app.get("/", security=security)
def oauth():
    return "oauth"


if __name__ == '__main__':
    app.run(debug=True)
