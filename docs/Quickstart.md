**`flask_openapi3`** based on [Flask](https://github.com/pallets/flask/)
and [Pydantic](https://github.com/pydantic/pydantic), So you can use it like Flask.

## A Minimal Application

Just like [Flask](https://flask.palletsprojects.com/en/latest/quickstart/#a-minimal-application), Create `hello.py`:

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

You will see the output information:

```
 * Serving Flask app 'just_flask' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

```

## REST API

You can use **`get`**, **`post`**, **`put`**, **`patch`**, **`delete`** REST API in `flask-openapi3`.

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

APIBlueprint based on [Flask Blueprint](https://flask.palletsprojects.com/en/latest/tutorial/views/#create-a-blueprint),
you should use **`register_api`** instead of  **`register_blueprint`**.

```python hl_lines="14"
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

api = APIBlueprint('book', __name__, url_prefix='/api')


@api.post('/book')
def create_book():
    return {"message": "success"}


# register api
app.register_api(api)

if __name__ == '__main__':
    app.run()
```

## Nested APIBlueprint

*New in v2.0.0*

Allow an **API Blueprint** to be registered on another **API Blueprint**.

For more information, please see [Flask Nesting Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/#nesting-blueprints).

```python hl_lines="21 22"
from flask_openapi3 import OpenAPI, APIBlueprint

app = OpenAPI(__name__)

api = APIBlueprint('book', __name__, url_prefix='/api/book')
api_english = APIBlueprint('english', __name__)
api_chinese = APIBlueprint('chinese', __name__)


@api_english.post('/english')
def create_english_book():
    return {"message": "english"}


@api_chinese.post('/chinese')
def create_chinese_book():
    return {"message": "chinese"}


# register nested api
api.register_api(api_english)
api.register_api(api_chinese)
# register api
app.register_api(api)

if __name__ == '__main__':
    app.run(debug=True)
```

## APIView

*New in v2.2.0*

Class-based API View, click [here](https://github.com/luolingchun/flask-openapi3/blob/APIView/examples/api_view_demo.py) go to the complete example:

```python
@api_view.route("/book")
class BookListAPIView:
    a = 1

    @api_view.doc(summary="get book list")
    def get(self, query: BookQuery):
        print(self.a)
        return query.json()

    @api_view.doc(summary="create book")
    def post(self, body: BookBody):
        """description for a created book"""
        return body.json()
```


## Async API

*New in v2.2.2*

Just use `async` when defining functions. More information goes to [Using async and await — Flask Documentation](https://flask.palletsprojects.com/en/latest/async-await/).

!!! info

    You need to manually install `asgiref` using pip:
    ```bash
    pip install flask-openapi3[async]
    
    # or
    pip install asgiref
    ```

```python hl_lines="2"
@app.post('/open/api')
async def post_openapi(body: Query):
    print(body)
    return 'POST, OpenAPI!'
```