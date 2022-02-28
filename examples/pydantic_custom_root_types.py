# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/2/27 15:26

from typing import List, Dict, Any

from pydantic import BaseModel, Extra

from flask_openapi3 import OpenAPI, Tag

app = OpenAPI(__name__)


class Sellout(BaseModel):
    a: str
    b: int


class SelloutList(BaseModel):
    __root__: List[Sellout]


class SelloutDict(BaseModel):
    __root__: Dict[str, Sellout]


class SelloutDict2(BaseModel):
    __root__: Dict[Any, Any]


class SelloutDict3(BaseModel):
    class Config:
        extra: Extra = Extra.allow


@app.post('/api/v1/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={'200': SelloutList}
          )
def post_sellout(body: SelloutList):
    print(body)
    return body.json()


@app.post('/api/v2/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={'200': SelloutDict}
          )
def post_sellout2(body: SelloutDict):
    print(body)
    return body.json()


@app.post('/api/v3/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout3(body: SelloutDict2):
    print(body)
    return body.json()


@app.post('/api/v4/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout4(body: SelloutDict3):
    print(body)
    return body.json()


if __name__ == '__main__':
    app.run(debug=True)
