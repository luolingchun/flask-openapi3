# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/12/19 10:34

from flask_openapi3.utils import normalize_name


def test_normalize_name():
    assert "List-Generic.Response_Detail_" == normalize_name("List-Generic.Response[Detail]")
