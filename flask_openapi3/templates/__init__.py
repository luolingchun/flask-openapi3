# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/2/16 9:46
openapi_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APIdoc</title>
    <link rel="shortcut icon" href="static/images/apidoc.svg">
    <style>
        body {
            background-color: #131417;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .box {
            width: 300px;
            height: 200px;
            background: #2c303a;
            border-radius: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            transform: scale(1);
            transition: all .3s ease;
        }

        .box:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #333743f0;
            cursor: pointer;
        }

        .box img {
            height: 64px;
            margin-bottom: 10px;
        }

        .box a {
            color: white;
            font-size: 24px;
            user-select: none;
        }
    </style>
</head>
<body>
<div class="grid">
    <div class="box" onclick="window.location.href= '{{ swagger_url }}';return false">
        <img src="static/images/swagger.svg" alt="Swagger UI">
        <a class="swagger">Swagger</a>
    </div>
    <div class="box" onclick="window.location.href= '{{ redoc_url }}';return false">
        <img src="static/images/redoc.svg" alt="ReDoc">
        <a class="redoc">ReDoc</a>
    </div>
    <div class="box" onclick="window.location.href= '{{ rapidoc_url }}';return false">
        <img src="static/images/rapidoc.svg" alt="RapiDoc">
        <a class="rapidoc">RapiDoc</a>
    </div>
    <div class="box" onclick="window.location.href= '{{ scalar_url }}';return false">
        <img src="static/images/scalar.svg" alt="Scalar">
        <a class="scalar">Scalar</a>
    </div>
</div>
</body>
</html>

"""
rapidoc_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1,user-scalable=yes">
    <title>RapiDoc</title>
    <link rel="shortcut icon" href="static/images/rapidoc.svg">
</head>
<body>
<rapi-doc spec-url='{{ api_doc_url }}'></rapi-doc>
<script>
    var rapiDoc = document.querySelector("rapi-doc");
    var specUrl = new URL("{{api_doc_url}}", window.location.href).href;
    rapiDoc.setAttribute("spec-url", specUrl);
</script>
<script src="static/js/rapidoc-min.js"></script>
</body>
</html>
"""
redoc_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>ReDoc</title>
    <link rel="shortcut icon" href="static/images/redoc.svg">
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!--link href="static/css/google-fonts.css" rel="stylesheet" -->
    <!-- ReDoc doesn't change outer page styles -->
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
<redoc spec-url='{{ api_doc_url }}'></redoc>
<script src="static/js/redoc.standalone.js"></script>
</body>
</html>
"""
swagger_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link rel="shortcut icon" href="static/images/swagger.svg">
    <link rel="stylesheet" type="text/css" href="static/css/swagger-ui.css">
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
<script src="static/js/swagger-ui-bundle.js"></script>
<script src="static/js/swagger-ui-standalone-preset.js"></script>
<script>
    const swagger_config = JSON.parse(`{{ swagger_config|tojson }}`);
    url = new URL("{{api_doc_url}}", window.location.href).href;
    window.onload = function () {
        // Begin Swagger UI call region
        window.ui = SwaggerUIBundle({
        ...{
            url: url,
            dom_id: "#swagger-ui",
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            docExpansion: "{{ doc_expansion }}",
            showExtensions: true,
            showCommonExtensions: true
        },
        ...swagger_config
        })
        // End Swagger UI call region
        const oauthConfig = JSON.parse(`{{ oauth_config|tojson }}`);
        if (oauthConfig != null) {
            window.ui.initOAuth({
                clientId: oauthConfig.clientId,
                clientSecret: oauthConfig.clientSecret,
                realm: oauthConfig.realm,
                appName: oauthConfig.appName,
                scopeSeparator: oauthConfig.scopeSeparator,
                scopes: oauthConfig.scopes,
                additionalQueryStringParams: oauthConfig.additionalQueryStringParams,
                usePkceWithAuthorizationCodeGrant: oauthConfig.usePkceWithAuthorizationCodeGrant
            })
        }
        const prefix = "flask-openapi3&"
        // authorize
        const old_authorize = window.ui.authActions.authorize;
        window.ui.authActions.authorize = function (security) {
            old_authorize(security)
            for (const key in security) {
                window.localStorage.setItem(prefix + key, JSON.stringify(security[key]))
            }
        }
        // logout
        const old_logout = window.ui.authActions.logout;
        window.ui.authActions.logout = function (security) {
            old_logout(security)
            for (const key of security) {
                window.localStorage.removeItem(prefix + key)
            }
        }
        // reload authorizations
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i)
            const value = JSON.parse(localStorage.getItem(key))
            key = key.replace(prefix, "")
            const security = {}
            security[key] = value
            old_authorize(security)
        }
    }
</script>
</body>
</html>
"""
scalar_html_string = """
<!doctype html>
<html>
    <head>
        <title>Scalar API</title>
        <meta charset="utf-8" />
        <meta
        name="viewport"
        content="width=device-width, initial-scale=1" />
        <link rel="shortcut icon" href="static/images/scalar.svg">
    </head>
    <body>
        <script
        id="api-reference"
        data-url="{{api_doc_url}}">
        </script>
        <script>
        const scalar_config = JSON.parse(`{{ scalar_config|tojson }}`);
        var configuration = {...scalar_config};
        var apiReference = document.getElementById('api-reference');
        apiReference.dataset.configuration = JSON.stringify(configuration);
        </script>
        <script src="static/js/scalar.standalone.js"></script>
    </body>
</html>
"""
