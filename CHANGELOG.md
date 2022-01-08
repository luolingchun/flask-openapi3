## v1.0.0 2022-??-??

- Add keyword parameters `summary` and `description`
- [#9](https://github.com/luolingchun/flask-openapi3/issues/9) Support for extra responses. Thinks @blynn99
- [#10](https://github.com/luolingchun/flask-openapi3/issues/10) Fix: header's title case. Thinks @rrr34
- Upgrade swagger UI v4.1.3
- Upgrade Redoc v2.0.0-rc.59
- Add rapidoc

### Breaking Changes

- Renamed `securitySchemes` to `security_schemes`
- Renamed `docExpansion` to `doc_expansion`

## v0.9.9 2021-12-09

- fix: default value in query and form model
- fix: empty form and body
- support `from __future__ import annotations`
- drop python36

## v0.9.8 2021-11-12

- add Configuration `docExpansion`
- query and form add array support

## v0.9.7 2021-08-19

- fix: path $ref
- fix: markdown enum

## v0.9.6 2021-08-18

- Export to markdown(Experimental)

## v0.9.5 2021-07-11

- remove `validate_resp` and add `VALIDATE_RESPONSE`

## v0.9.4 2021-07-03

- OpenAPI add responses and APIBlueprint add abp_responses
- fix: validate response error when responses is empty dict
- [#3](https://github.com/luolingchun/flask-openapi3/issues/3) endpoint and APIBlueprint add `doc_ui`. Thinks
  @DerManoMann
- [#4](https://github.com/luolingchun/flask-openapi3/issues/4) fix: response description. Thinks @DerManoMann
- [#5](https://github.com/luolingchun/flask-openapi3/issues/5) add custom parameter `oauth_config`. Thinks @DerManoMann
- [#6](https://github.com/luolingchun/flask-openapi3/issues/6) support validation Flask Response. Thinks @DerManoMann
- [#7](https://github.com/luolingchun/flask-openapi3/issues/7) fix: response validation does not work when uses
  http.HTTPStatus enums as status_code. Thinks @DerManoMann

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
