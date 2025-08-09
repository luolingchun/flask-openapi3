# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:54

from pydantic import BaseModel

from .header import Header
from .link import Link
from .media_type import MediaType
from .reference import Reference


class Response(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#response-object
    """

    description: str
    headers: dict[str, Header | Reference] | None = None
    content: dict[str, MediaType] | None = None
    links: dict[str, Link | Reference] | None = None

    model_config = {"extra": "allow"}
