# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:41
from typing import TYPE_CHECKING, Union

from pydantic import BaseModel

from .reference import Reference

if TYPE_CHECKING:  # pragma: no cover
    from .header import Header
else:
    Header = "Header"


class Encoding(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#encoding-object
    """

    contentType: str | None = None
    headers: dict[str, Union[Header, Reference]] | None = None
    style: str | None = None
    explode: bool | None = None
    allowReserved: bool = False

    model_config = {"extra": "allow"}
