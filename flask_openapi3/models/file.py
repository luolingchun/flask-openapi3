# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/11 16:17
from werkzeug.datastructures import FileStorage as _FileStorage


class FileStorage(_FileStorage):
    """
    An uploaded file included as part of the request data.
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            format="binary",
            type="string"
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, _FileStorage):
            raise TypeError('werkzeug.datastructures.FileStorage required')

        return v
