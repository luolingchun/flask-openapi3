**`flask_openapi3`** 基于 [Flask](https://github.com/pallets/flask/)
和 [Pydantic](https://github.com/pydantic/pydantic)，因此你可以像使用Flask一样使用 **`flask_openapi3`**。

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

你将会看到输出信息：

```
 * Serving Flask app 'just_flask' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

```

## REST API

你可以在 `flask-openapi3` 中使用 **`get`**，**`post`**，**`put`**，**`patch`**，**`delete`** 等 REST API 。

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

[APIBlueprint](./Reference/APIBlueprint.md)
基于 [Flask Blueprint](https://flask.palletsprojects.com/en/latest/tutorial/views/#create-a-blueprint)，
你应该使用 **`register_api`** 来代替 **`register_blueprint`**。

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

## 嵌套 APIBlueprint

允许一个 **API Blueprint** 被另一个 **API Blueprint** 注册。

更多信息请查看 [Flask Nesting Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/#nesting-blueprints)。

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

[基于类的 API 视图](./Reference/APIView.md)， 点击[这里](https://github.com/luolingchun/flask-openapi3/blob/APIView/examples/api_view_demo.py) 查看完整示例:

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
        """description for create book"""
        return body.json()
```

## 异步 API

在定义函数时使用 `async`。 更多信息参考 [Using async and await — Flask Documentation](https://flask.palletsprojects.com/en/latest/async-await/)。

!!! info

    你需要使用 pip 手动安装 `asgiref`:
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