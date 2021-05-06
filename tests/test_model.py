# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
from enum import Enum

from pydantic import Field, BaseModel


class E(Enum):
    e1 = 1
    e2 = 2


class Test(BaseModel):
    a: int
    b: str = Field(default='222')
    c: str = Field(None)


class TTT(Test):
    d: str = '1'


if __name__ == '__main__':
    ttt = TTT(a=1, d='111')
    print(ttt.dict(by_alias=True,exclude_none=True))
