# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:41
from typing import TYPE_CHECKING, Dict, Optional, Union

from pydantic import BaseModel

from .reference import Reference

if TYPE_CHECKING:
    from .header import Header
else:
    Header = "Header"


class Encoding(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#encoding-object
    """

    contentType: Optional[str] = None
    headers: Optional[Dict[str, Union[Header, Reference]]] = None
    style: Optional[str] = None
    explode: bool = False
    allowReserved: bool = False

    class Config:
        extra = "allow"
