# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:54
from typing import Dict, Optional, Union

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
    headers: Optional[Dict[str, Union[Header, Reference]]] = None
    content: Optional[Dict[str, MediaType]] = None
    links: Optional[Dict[str, Union[Link, Reference]]] = None

    model_config = {
        "extra": "allow"
    }
