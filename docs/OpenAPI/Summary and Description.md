You need add docs to the view-func. The first line is the **summary**, and the rest is the **description**. like this:

```python hl_lines="3 4 5 6"
@app.get('/book/<int:bid>', tags=[book_tag], responses={"200": BookResponse}, security=security)
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}
```

![image-20210605115557426](../assets/image-20210605115557426.png)

*New in v1.0.0*

Now keyword parameters `summary` and `description` is supported, it will be take first.

```python hl_lines="1"
@app.get('/book/<int:bid>', tags=[book_tag], summary="new summary", description='new description', responses={"200": BookResponse}, security=security)
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}
```

![Snipaste_2022-03-19_15-10-06.png](../assets/Snipaste_2022-03-19_15-10-06.png)