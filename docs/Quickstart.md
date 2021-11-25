**`flask_openapi3`** based on [Flask](https://github.com/pallets/flask/) and [pydantic](https://github.com/samuelcolvin/pydantic), So you can use it like Flask.

## A Minimal Application

just like [Flask](https://flask.palletsprojects.com/en/latest/quickstart/#a-minimal-application), Create `hello.py`:

``` python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
```

And then run it:

```shell
python hello.py
```
You will see the output:

```
  __ _           _                                             _  _____
 / _| |         | |                                           (_)|____ |
| |_| | __ _ ___| | ________ ___  _ __   ___ _ __   __ _ _ __  _     / /
|  _| |/ _` / __| |/ /______/ _ \| '_ \ / _ \ '_ \ / _` | '_ \| |    \ \
| | | | (_| \__ \   <      | (_) | |_) |  __/ | | | (_| | |_) | |.___/ /
|_| |_|\__,_|___/_|\_\      \___/| .__/ \___|_| |_|\__,_| .__/|_|\____/
                                 | |                    | |
                                 |_|                    |_|

 * Serving Flask app 'just_flask' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## RESTful API

You can use **`get`**, **`post`**, **`put`**, **`patch`**, **`delete`** RESTful API in `flask-openapi3`.

```python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


@app.get('/book')
def get_books():
    return ["book1", "book2"]


@app.post('/book')
def create_book():
    return {"message": "success"}

if __name__ == '__main__':
    app.run()
```

## APIBlueprint

APIBlueprint based on [Flask Blueprint](https://flask.palletsprojects.com/en/latest/tutorial/views/#create-a-blueprint), you should use **`app.register_api`** instead of  **`app.register_blueprint`**.

```python hl_lines="14"
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

api = APIBlueprint('/book', __name__, url_prefix='/api')


@api.post('/book')
def create_book():
    return {"message": "success"}


# register api
app.register_api(api)

if __name__ == '__main__':
    app.run()
```
