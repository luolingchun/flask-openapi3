# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45
from typing import Optional

from pydantic import BaseModel


class License(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#license-object
    """

    name: str
    identifier: Optional[str] = None
    url: Optional[str] = None

    model_config = {
        "extra": "allow"
    }
