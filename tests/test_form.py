# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/8/6 13:47
from enum import Enum
from typing import List, Union, Dict, Any

import pytest
from pydantic import BaseModel

from flask_openapi3 import FileStorage, OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class MetadataParameter(BaseModel):
    tag: str


class MetadataParameter2(BaseModel):
    tag2: str


class FileType(int, Enum):
    a = 1
    b = 2


class FormParameters(BaseModel):
    file: FileStorage
    file_list: List[FileStorage]
    file_type: FileType
    number: float
    number_list: List[float]
    boolean: bool
    boolean_list: List[bool]
    digit: int
    digit_list: List[int]
    string: str
    string_list: List[str]
    obj: Dict[Any, Any]
    parameter: MetadataParameter
    parameter_dict: Dict[str, MetadataParameter]
    parameter_list: List[MetadataParameter]
    parameter_list_union: List[Union[bool, float, str, int, FileType, MetadataParameter]]
    parameter_union: Union[MetadataParameter, MetadataParameter2]
    union_all: Union[str, int, float, bool, FileType, MetadataParameter]
    none: None = None
    default_value: str = "default_value"


@app.post("/example")
def complex_form_example(form: FormParameters):
    print(form.model_dump())
    return "ok"


def test_openapi(client):
    from io import BytesIO
    data = {
        "boolean": "true",
        "boolean_list": [True, False],
        "digit": "1",
        "digit_list": ["2", "3"],
        "file": (BytesIO(b"post-data"), "filename"),
        "file_list": [(BytesIO(b"post-data"), "filename"), (BytesIO(b"post-data"), "filename")],
        "file_type": "1",
        "none": "null",
        "number": "1.2",
        "number_list": ["3.4", "5.6"],
        "obj": '{"a": 2}',
        "parameter": '{"tag": "string"}',
        "parameter_dict": '{"additionalProp1": {"tag": "string"}, "additionalProp2": {"tag": "string"},'
                          '"additionalProp3": {"tag": "string"}}',
        "parameter_list": ['{"tag": "string"}', '{"tag": "string"}'],
        "parameter_list_union": ["ok", '{"tag": "string"}', "7.8"],
        "parameter_union": '{"tag2": "string"}',
        "union_all": "true",
        "string": "a",
        "string_list": ["a", "b", "c"]
    }
    resp = client.post("/example", data=data, content_type="multipart/form-data")
    print(resp.text)
    assert resp.status_code == 200


if __name__ == '__main__':
    app.run(debug=True)
