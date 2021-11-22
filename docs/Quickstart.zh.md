**`flask_openapi3`** 基于 [Flask](https://github.com/pallets/flask/) 和 [pydantic](https://github.com/samuelcolvin/pydantic)，因此你可以像使用Flask一样使用它。

## 最小应用

像 [Flask](https://flask.palletsprojects.com/en/latest/quickstart/#a-minimal-application) 一样，创建 `hello.py`:

``` python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
```

然后运行：

```shell
python hello.py
```
你将会看到输出。

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

你可以在 `flask-openapi3` 中使用 **`get`**，**`post`**，**`put`**，**`patch`**，**`delete`** 等 RESTful API 。

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

APIBlueprint 基于 [Flask Blueprint](https://flask.palletsprojects.com/en/latest/tutorial/views/#create-a-blueprint)，你应该使用 **`app.register_api`** 来代替 **`app.register_blueprint`**.

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
