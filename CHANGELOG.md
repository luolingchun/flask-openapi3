## v4.3.0 2025-10-18

- Fix ValidationError schema to match Pydantic v2 format by @bastien-pruvost in #232
- Bump actions/checkout from 4 to 5 by @dependabot[bot] in #234
- Support optional lists by @Qblack in #237
- Bump actions/stale from 9 to 10 by @dependabot[bot] in #239
- Bump actions/setup-python from 5 to 6 by @dependabot[bot] in #238
- [#240] Fix for br tag rendering by @zakmatik in #241
- Use uv by @luolingchun in #235
- Drop support for Python 3.9 and Support for Python 3.14 by @luolingchun in #233
- ISSUE-220 allow for response validation by @mr-tabasco in #225
- WIP Add support for const by @githubjakob in #243

## v4.2.1 2025-07-19

- Fixes issue where register_api isn't idempotent by @zakmatik in #230
- Make validate_request pass on existing kwargs but remove those part of path by @puittenbroek in #227

## v4.2.0 2025-06-21

- fix(models): enable 'populate_by_name' to alias fields correctly by @omikader in #221
- operation_id_callback with blueprint name and func name by @luolingchun in #224
- Delay throwing validation error by @luolingchun in #223

## v4.1.0 2025-02-08

- Support for Python 3.13 by @luolingchun in #200
- Fix query, form, header model extra not honored by @luolingchun in #201
- Better APISpec init to allow to modify it before generating spec_json. by @ddorian in #195
- Schema.maximum type float -> int | float by @ddorian in #217
- Allow url_prefix to be set during API/APIView registration by @luolingchun in #215
- Drop support for Python 3.8 by @luolingchun in #199

## v4.0.3 2024-11-23

- Add PrefixItems to Schema Model for use with Tuple types by @JesseDeLoore in #197

## v4.0.2 2024-11-10

- Reuse schema["title"] if it's defined by @ddorian in #186
- Simple webhook schema by @ddorian in #191
- Fix missing Field.default when it's value is None in openapi spec by @ddorian in #189
- ServerVariable.enum should be optional by @luolingchun in #194

## v4.0.1 2024-10-05

- Fix alias in query and form by @luolingchun in #184

## v4.0.0 2024-09-29

* Support plugins for ui templates by @luolingchun in #151
* Add py.typed marker file for PEP-561 support by @luolingchun in #160
* Use ruff instead of flake8 by @luolingchun in #164
* Remove experimental export markdown by @luolingchun in #161
* Fix `populate_by_name` when execute `model_validate` by @luolingchun in #167
* Update docs by @luolingchun in #155
* Fix __get_pydantic_core_schema__ by @luolingchun in #179
* Fix list with default value by @luolingchun in #180

## v4.0.0rc3 2024-08-31

- Add py.typed marker file for PEP-561 support by @luolingchun in #160
- Use ruff instead of flake8 by @luolingchun in #164
- Remove experimental export markdown by @luolingchun in #161
- Fix `populate_by_name` when execute `model_validate` by @luolingchun in #167
- Optimize performance and unit testing by @luolingchun in #155

## v4.0.0rc2 2024-06-16

- Fix empty list in body by @luolingchun in #154

## v4.0.0rc1 2024-06-02

- Support plugins for ui templates
- Support for OPENAPI_HTML_STRING in app.config

## v3.1.3 2024-06-16

- Fix empty list in body by @luolingchun in #154

## v3.1.2 2024-06-02

- Support SWAGGER_CONFIG and OAUTH_CONFIG in app.config by @luolingchun in #153

**DeprecationWarning**

- The `api_doc_url` is deprecated in v4.x, use `doc_url` instead.
- The `swagger_url` is deprecated in v4.x.
- The `redoc_url` is deprecated in v4.x.
- The `rapidoc_url` is deprecated in v4.x.
- The `oauth_config` is deprecated in v4.x, use `app.config['OAUTH_CONFIG']` instead.
- The `doc_expansion` is deprecated in v4.x, use `app.config['SWAGGER_CONFIG']` instead.
- The `swagger_config` is deprecated in v4.x, use `app.config['SWAGGER_CONFIG']` instead.
- The `ui_templates` is deprecated in v4.x.

## v3.1.1 2024-04-21

- Wrong types of exclusiveMinimum & exclusiveMaximum fields in Schema class by @Lavertis in #149

## v3.1.0 2024-03-24

- Add the swagger_config parameter to configure the swagger ui by @luolingchun in #146
- Use full links in Swagger and RapiDoc
- Upgrade Redoc to 2.1.3
- Upgrade Swagger to 5.12.0

**DeprecationWarning**

- The doc_expansion parameter is deprecated; use swagger_config instead.

## v3.0.2 2024-01-28

- Fix missing Pydantic Calculated Fields (#141). Thanks, @thebmw.

## v3.0.1 2023-11-26

- Fix the same operationId in APIBlueprint (#133). Thanks, @fluffybrain3.
- Make body required false (#130). Thanks, @styper.
- The default value defined in the form is invalid (#129). Thanks, @seekplum.

## v3.0.0 2023-10-22

- Upgrade pydantic to v2.
- Remove deprecated code.
- Drop support for Python 3.7.
- support for raw requests (#109).
- Upgrade Swagger UI v5.9.0.
- Upgrade Redoc v2.1.2
- Update RapiDoc 9.3.4.
- [#105](https://github.com/luolingchun/flask-openapi3/pull/105) Supports valid properties only. Thanks, @ota42y.
- [#106](https://github.com/luolingchun/flask-openapi3/pull/106) Bugfix for parameter object. Thanks, @ota42y.
- [#107](https://github.com/luolingchun/flask-openapi3/pull/107) Bugfix for generics class. Thanks, @ota42y.
- [#114](https://github.com/luolingchun/flask-openapi3/pull/114) Support Flask 3.0.
- [#118](https://github.com/luolingchun/flask-openapi3/discussions/118) Fix missed components schemas in
  ValidationErrorModel. Thanks, @SeFeX.
- [#122](https://github.com/luolingchun/flask-openapi3/issues/122) Skip 422 response non parameters. Thanks, @Danielsn1.

## v3.0.0rc2 2023-10-03

- [#105](https://github.com/luolingchun/flask-openapi3/pull/105) Supports valid properties only. Thanks, @ota42y.
- [#106](https://github.com/luolingchun/flask-openapi3/pull/106) Bugfix for parameter object. Thanks, @ota42y.
- [#107](https://github.com/luolingchun/flask-openapi3/pull/107) Bugfix for generics class. Thanks, @ota42y.
- [#114](https://github.com/luolingchun/flask-openapi3/pull/114) Support Flask 3.0.

## v3.0.0rc1 2023-09-03

- Upgrade pydantic to v2
- Remove deprecated code
- Drop support for Python 3.7

## v2.5.5 2023-11-26

- Fix the same operationId in APIBlueprint (#133). Thanks, @fluffybrain3.
- Make body required false (#130). Thanks, @styper.
- The default value defined in the form is invalid (#129). Thanks, @seekplum.

## v2.5.4 2023-10-22

- [#118](https://github.com/luolingchun/flask-openapi3/discussions/118) Fix missed components schemas in
  ValidationErrorModel. Thanks, @SeFeX.
- [#122](https://github.com/luolingchun/flask-openapi3/issues/122) Skip 422 response non parameters. Thanks, @Danielsn1.

## v2.5.3 2023-10-03

- [#105](https://github.com/luolingchun/flask-openapi3/pull/105) Supports valid properties only. Thanks, @ota42y.
- [#106](https://github.com/luolingchun/flask-openapi3/pull/106) Bugfix for parameter object. Thanks, @ota42y.
- [#107](https://github.com/luolingchun/flask-openapi3/pull/107) Bugfix for generics class. Thanks, @ota42y.

## v2.5.2 2023-08-13

- [#97](https://github.com/luolingchun/flask-openapi3/issues/97) Fix response miss description. Thanks, @tekrei.

## v2.5.1 2023-08-07

- [#95](https://github.com/luolingchun/flask-openapi3/pull/95) Added ability to deserialize complex form parameter
  objects. Thanks, @BlackGad.

## v2.5.0 2023-08-02

- [#79](https://github.com/luolingchun/flask-openapi3/discussions/79) Support `by_alias` in Model Config. Thanks,
  @candleindark.
- [#82](https://github.com/luolingchun/flask-openapi3/issues/82) Fix parameter in url_prefix. Thanks, @riedgar-ms.
- [#83](https://github.com/luolingchun/flask-openapi3/pull/83) Be able to change 422 validation errors to other http
  response status. Thanks, @CostcoFanboy.
- [#86](https://github.com/luolingchun/flask-openapi3/issues/86) Responses key supports both string, int, and
  HTTPStatus. Thanks, @CostcoFanboy.

## v2.4.0 2023-06-04

- [#72](https://github.com/luolingchun/flask-openapi3/pull/72) security_schemes(SecurityScheme) supports a json format.
- [#68](https://github.com/luolingchun/flask-openapi3/pull/68) feat: Add operation_id_callback. Thanks, @BoyanYK.
- [#64](https://github.com/luolingchun/flask-openapi3/pull/64) Explains the usage of flask openapi command more clearly.
  Thanks, @candleindark.
- [#75](https://github.com/luolingchun/flask-openapi3/pull/75) Init view_class and pass view_kwargs. Thanks, @stufisher.
- [#70](https://github.com/luolingchun/flask-openapi3/issues/70) Support for Specification Extensions in OpenAPI Object
  and Operation Object. Thanks, @simonblund.
- [#73](https://github.com/luolingchun/flask-openapi3/issues/73) BaseModel Config support openapi_extra.
- Merge `extra_responses` to `responses` and deprecate `extra_responses`.

**DeprecationWarning:**

- Add DeprecationWarning to `APIKey`, `HTTPBase`, `OAuth2`, `OpenIdConnect`, `HTTPBearer` that will be deprecated in
  v3.0.
- Add DeprecationWarning to `extra_form`, `extra_body` and `extra_responses` that will be deprecated in v3.0.

## v2.3.2 2023-04-03

- [#61](https://github.com/luolingchun/flask-openapi3/issues/61) Fix headers with pydantic alias

## v2.3.1 2023-02-13

- remove * in install_requires for setuptools 67+

## v2.3.0 2023-02-12

- Support for custom UI templates (#55)
- endpoint index rename to openapi
- fix missing enum in component schemas

## v2.2.2 2023-01-01

- Fix async
- Fix duplicate tags

## v2.2.1 2022-11-23

- Add dependent files

## v2.2.0 2022-11-14

- support APIView
- Add mypy
- Support for python 3.11
- Upgrade Swagger UI 4.15.5
- Upgrade Redoc UI 2.0.0

## v2.1.1 2022-10-12

- [#41](https://github.com/luolingchun/flask-openapi3/issues/41) Set the `requestBody required` default value to True.
  Thanks, @Colin-b
- Fix multi decorator for api
- [#42](https://github.com/luolingchun/flask-openapi3/issues/42) Fix required header is not found when `_` in header
  field. Thanks, @elirud

## v2.1.0 2022-09-04

- [#36](https://github.com/luolingchun/flask-openapi3/issues/36) Add extra_form for operation. Thanks, @Colin-b
- [#36](https://github.com/luolingchun/flask-openapi3/issues/36) Add extra_body for operation. Thanks, @Colin-b
- Add external_docs for operation
- Add servers for operation
- Support to parse extra field in parameters
- [#35](https://github.com/luolingchun/flask-openapi3/issues/35) Fixed extra_responses can now be used to set every
  field in Response. Thanks, @Colin-b
- Upgrade Swagger UI 4.14.0
- Upgrade Redoc UI 2.0.0-rc.76
- Upgrade RapiDoc UI 9.3.3

### Breaking Changes

- [#39](https://github.com/luolingchun/flask-openapi3/issues/39) Remove configuration FLASK_OPENAPI_VALIDATE_RESPONSE

## v2.0.1 2022-08-07

- [#32](https://github.com/luolingchun/flask-openapi3/issues/32) Fix: parse_rule is deprecated in werkzeug>=2.2.0.

## v2.0.0 2022-06-26

- [#26](https://github.com/luolingchun/flask-openapi3/issues/26) Fixed: Body throws exception when receiving str instead
  of dict. Thanks, @nor3th
- [#23](https://github.com/luolingchun/flask-openapi3/pull/23) Fixed externalDocs support. Thanks, @dvaerum
- [#28](https://github.com/luolingchun/flask-openapi3/pull/28) Fixed to enable `__root__` property when validation
  responses. Thanks, @dvaerum
- [#17](https://github.com/luolingchun/flask-openapi3/issues/17) Support for Nested APIBlueprint enhancement. Thanks,
  @dvaerum
- [#29](https://github.com/luolingchun/flask-openapi3/pull/29) Support disable warnings. Thanks, @dvaerum
- Support for empty response body. Thanks, @dvaerum
- Support reload authorizations in Swagger UI
- Add `flask openapi` command
- Add options in view functions
- Upgrade flask to v2.x

### Breaking Changes

- Remove export markdown to `flask openapi` command
- Configuration `VALIDATE_RESPONSE` rename to `FLASK_OPENAPI_VALIDATE_RESPONSE`

## v1.1.4 2022-05-05

- fix: Trailing slash in APIBlueprint

## v1.1.3 2022-05-01

- fix: Find globalns for the unwrapped func
- [#19](https://github.com/luolingchun/flask-openapi3/issues/19) fix: Trailing slash in APIBlueprint. Thanks, @ev-agelos
- add description for UnprocessableEntity
- remove printouts in `__init__.py`

## v1.1.2 2022-04-01

- [#16](https://github.com/luolingchun/flask-openapi3/issues/16) Fix fileStorage list is not supported. Thanks, @tekrei

## v1.1.0 2022-03-13

- [#13](https://github.com/luolingchun/flask-openapi3/issues/13) drop support for flask 1.0.x. Thanks, @danmur
- [#15](https://github.com/luolingchun/flask-openapi3/pull/15) Fix to enable BaseModel with `__root__` property. Thanks,
  @tarcisiojr
- [#14](https://github.com/luolingchun/flask-openapi3/pull/14) Custom parameters: doc_prefix, api_doc_url, swagger_url,
  redoc_url, rapidoc_url. Thanks, @barryrobison
- Upgrade swagger UI v4.6.2
- Upgrade Redoc v2.0.0-rc.63
- Upgrade RapiDoc v9.2.0

## v1.0.1 2022-02-12

- add operation_id for OpenAPI Specification

## v1.0.0 2022-01-11

- [#10](https://github.com/luolingchun/flask-openapi3/issues/10) Fix: header's title case. Thanks, @rrr34
- [#9](https://github.com/luolingchun/flask-openapi3/issues/9) Support for extra responses. Thanks, @blynn99
- [#12](https://github.com/luolingchun/flask-openapi3/pull/12) Support for path operation field deprecated. Thanks,
  @blynn99
- Add keyword parameters `summary` and `description`
- Add servers for OpenAPI
- Upgrade swagger UI v4.1.3
- Upgrade Redoc v2.0.0-rc.59
- Add rapidoc

### Breaking Changes

- Renamed `securitySchemes` to `security_schemes`
- Renamed `docExpansion` to `doc_expansion`

## v0.9.9 2021-12-09

- fix: default value in a query and form model
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
- [#3](https://github.com/luolingchun/flask-openapi3/issues/3) endpoint and APIBlueprint add `doc_ui`. Thanks,
  @DerManoMann
- [#4](https://github.com/luolingchun/flask-openapi3/issues/4) fix: response description. Thanks, @DerManoMann
- [#5](https://github.com/luolingchun/flask-openapi3/issues/5) add custom parameter `oauth_config`. Thanks, @DerManoMann
- [#6](https://github.com/luolingchun/flask-openapi3/issues/6) support validation Flask Response. Thanks, @DerManoMann
- [#7](https://github.com/luolingchun/flask-openapi3/issues/7) fix: response validation does not work when uses
  http.HTTPStatus enums as status_code. Thanks, @DerManoMann

## v0.9.3 2021-06-08

- APIBlueprint adds abp_tags and abp_security
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
