# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/8/18 17:19
from enum import Enum

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info

app = OpenAPI(
    __name__,
    info=Info(title='Enum demo', version='1.0.0')
)


class Language(str, Enum):
    cn = 'Chinese'
    en = 'English'


class Path(BaseModel):
    language: Language = Field(..., description='Language')


@app.get('/<language>')
def get_enum(path: Path):
    print(path)
    return {}


if __name__ == '__main__':
    app.run(debug=True)
