# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/10 14:51
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class UnprocessableEntity(BaseModel):
    loc: Optional[List[str]] = Field(None, title="Location")
    msg: Optional[str] = Field(None, title="Message")
    type_: Optional[str] = Field(None, title="Error Type")
    ctx: Optional[Dict[str, Any]] = Field(None, title="Error context")
