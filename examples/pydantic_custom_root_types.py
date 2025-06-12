# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/2/27 15:26
import logging
from typing import Any

from pydantic import BaseModel, RootModel

from flask_openapi3 import OpenAPI, Tag


logger = logging.getLogger(__name__)

app = OpenAPI(__name__)


class Sellout(BaseModel):
    a: str
    b: int


class SelloutList(RootModel):
    root: list[Sellout]


class SelloutDict(RootModel):
    root: dict[str, Sellout]


class SelloutDict2(RootModel):
    root: dict[Any, Any]


class SelloutDict3(BaseModel):
    model_config = {"extra": "allow"}


@app.post("/api/v1/sellouts", tags=[Tag(name="Sellout", description="Loren.")], responses={200: SelloutList})
def post_sellout(body: SelloutList):
    logger.info(body)
    return body.model_dump()


@app.post("/api/v2/sellouts", tags=[Tag(name="Sellout", description="Loren.")], responses={200: SelloutDict})
def post_sellout2(body: SelloutDict):
    logger.info(body)
    return body.model_dump()


@app.post("/api/v3/sellouts", tags=[Tag(name="Sellout", description="Loren.")])
def post_sellout3(body: SelloutDict2):
    logger.info(body)
    return body.model_dump()


@app.post("/api/v4/sellouts", tags=[Tag(name="Sellout", description="Loren.")])
def post_sellout4(body: SelloutDict3):
    logger.info(body)
    return body.model_dump()


if __name__ == "__main__":
    app.run(debug=True)  # nosec
