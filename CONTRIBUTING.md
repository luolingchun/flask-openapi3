## Contributing Guide

Thank you for contributing to Flask OpenAPI.

1. [Create a new issue](https://github.com/luolingchun/flask-openapi3/issues/new)
2. [Fork and Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

Before submitting pr, you need to complete the following two steps：

1. Running the tests

    ```bash
    pytest tests
    flake8 flask_openapi3 tests examples
    ```
    
2. Building the docs

   Serve the live docs with [Material for MkDocs](https://github.com/squidfunk/mkdocs-material), and make sure it's correct.

    ```bash
    mkdocs serve
    ```
