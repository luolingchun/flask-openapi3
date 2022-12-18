## Use `orjson`

```python hl_lines="17"
import orjson
from flask.json.provider import JSONProvider


class OrJSONProvider(JSONProvider):
    # https://github.com/ijl/orjson#option
    option = orjson.OPT_INDENT_2

    def dumps(self, obj, **kwargs):
        return orjson.dumps(obj, option=self.option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)
    
app = OpenAPI(__name__, info=info)
# use orjson
orjson_provider = OrJSONProvider(app)
app.json = orjson_provider
```

## Use `ujson`

```python hl_lines="24"
import ujson
from flask.json.provider import JSONProvider

class UJSONProvider(JSONProvider):
    # https://github.com/ultrajson/ultrajson
    encode_html_chars = False
    ensure_ascii = False
    indent = 4

    def dumps(self, obj, **kwargs):
        option = {
            "encode_html_chars": self.encode_html_chars,
            "ensure_ascii": self.ensure_ascii,
            "indent": self.indent
        }
        return ujson.dumps(obj, **option)

    def loads(self, s, **kwargs):
        return ujson.loads(s)
    
    
app = OpenAPI(__name__, info=info)
# use ujson
ujson_provider = UJSONProvider(app)
app.json = ujson_provider
```