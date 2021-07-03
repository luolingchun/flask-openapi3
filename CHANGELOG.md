## v0.9.4 2021-07-03

- OpenAPI add responses and APIBlueprint add abp_responses
- fix: validate response error when responses is empty dict
- [#3](https://github.com/luolingchun/flask-openapi3/issues/3) endpoint and APIBlueprint add `doc_ui`. Thinks @DerManoMann 
- [#4](https://github.com/luolingchun/flask-openapi3/issues/4) fix: response description. Thinks @DerManoMann 
- [#5](https://github.com/luolingchun/flask-openapi3/issues/5) add custom parameter `oauth_config`. Thinks @DerManoMann 
- [#6](https://github.com/luolingchun/flask-openapi3/issues/6) support validation Flask Response. Thinks @DerManoMann 
- [#7](https://github.com/luolingchun/flask-openapi3/issues/7) fix: response validation does not work when uses http.HTTPStatus enums as status_code. Thinks @DerManoMann 

## v0.9.3 2021-06-08

- APIBlueprint add abp_tags and abp_security
- fix: tags de-duplication
- fix: operation summary and description

## v0.9.2 2021-05-17

- fix: _do_decorator
- add doc_ui args. support close swagger UI and redoc

## v0.9.1 2021-05-16

- fix：request data is None 
- json-->body
- set 422 Content-Type application/json
- raise response validate exception
- fix: TypeError: issubclass() arg 1 must be a class

## v0.9.0 2021-05-13

- first version