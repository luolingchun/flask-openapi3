# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/10 14:51
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class UnprocessableEntity(BaseModel):
    # More information: https://pydantic-docs.helpmanual.io/usage/models/#error-handling
    loc: Optional[List[str]] = Field(None, title="Location", description="the error's location as a list. ")
    msg: Optional[str] = Field(None, title="Message", description="a computer-readable identifier of the error type.")
    type_: Optional[str] = Field(None, title="Error Type", description="a human readable explanation of the error.")
    ctx: Optional[Dict[str, Any]] = Field(
        None,
        title="Error context",
        description="an optional object which contains values required to render the error message."
    )
