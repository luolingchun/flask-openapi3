# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/6/21 15:54
from enum import Enum
from http import HTTPStatus

HTTP_STATUS = {str(status.value): status.phrase for status in HTTPStatus}


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"
