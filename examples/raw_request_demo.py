# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/9/12 17:19
import logging

from flask_openapi3 import OpenAPI, RawModel


app = OpenAPI(__name__)


logger = logging.getLogger(__name__)


class BookRaw(RawModel):
    mimetypes = ["text/csv", "application/json"]


@app.post("/book")
def get_book(raw: BookRaw):
    # raw equals to flask.request
    logger.info(raw.data)
    logger.info(raw.mimetype)
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)  # nosec
