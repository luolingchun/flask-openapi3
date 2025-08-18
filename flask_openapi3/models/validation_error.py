# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/10 14:51
from typing import Any

from pydantic import BaseModel, Field


class ValidationErrorModel(BaseModel):
    # More information: https://docs.pydantic.dev/latest/concepts/models/#error-handling
    type: str = Field(..., title="Error Type", description="A computer-readable identifier of the error type.")
    loc: list[Any] = Field(..., title="Location", description="The error's location as a list.")
    msg: str = Field(..., title="Message", description="A human readable explanation of the error.")
    input: Any = Field(..., title="Input", description="The input provided for validation.")
    url: str | None = Field(None, title="URL", description="The URL to further information about the error.")
    ctx: dict[str, Any] | None = Field(
        None,
        title="Error context",
        description="An optional object which contains values required to render the error message.",
    )


# backward compatibility
UnprocessableEntity = ValidationErrorModel
