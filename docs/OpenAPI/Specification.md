## Specification

If you need the complete Specification(json) , go to http://127.0.0.1:5000/openapi/openapi.json

**command: `flask openapi`**

*New in v2.0.0*

The `flask openapi` command will export the OpenAPI Specification to console when you execute the command:

```
flask openapi
```

Execute `flask openapi --help` for more information:

```
flask openapi --help

Usage: flask openapi [OPTIONS]

  Export the OpenAPI Specification to console or a file

Options:
  -o, --output PATH               The output file path.
  -f, --format [json|yaml|markdown]
                                  The output file format.
  -i, --indent INTEGER            The indentation for JSON dumps.
  -a, --ensure_ascii              Ensure ASCII characters or not. Defaults to
                                  False.
  --help                          Show this message and exit.

```

!!! info

    You need to manually install `pyyaml` using pip:
    ```bash
    pip install flask-openapi3[yaml]
    
    # or
    pip install pyyaml
    ```

## doc_ui

You can pass `doc_ui=False` to disable the `OpenAPI spec` when init `OpenAPI `.

```python
app = OpenAPI(__name__, info=info, doc_ui=False)
```

*New in v0.9.4*

You can also use `doc_ui` in endpoint or when initializing `APIBlueprint`.

```python hl_lines="4 9"
api = APIBlueprint(
    '/book',
    __name__,
    doc_ui=False
)

# or

@api.get('/book', doc_ui=False)
def get_book():
    ...
```

## deprecated

*New in v1.0.0*

`deprecated`: mark as deprecated support. Default to not True.

```python
@app.get('/book', deprecated=True)
def get_books(query: BookQuery):
    ...
```

## doc_expansion

Just for Swagger UI.

String=["list", "full", "none"].

Controls the default expansion setting for the operations and tags. It can be 'list' (expands only the tags),
'full' (expands the tags and operations) or 'none' (expands nothing).

More information to
see [Configuration](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).

```python
app = OpenAPI(__name__, info=info, doc_expansion='full')
```

## servers

An array of Server Objects, which provide connectivity information to a target server. If the server's property is not
provided, or is an empty array, the default value would be a Server Object with an url value of /.

```python
from flask_openapi3 import OpenAPI, Server

servers = [
    Server(url='http://127.0.0.1:5000'),
    Server(url='https://127.0.0.1:5000'),
]
app = OpenAPI(__name__, info=info, servers=servers)
```