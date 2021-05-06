# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 14:53

from pydantic import BaseModel, Field


class JsonResponse(BaseModel):
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="信息")
