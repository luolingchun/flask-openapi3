# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/11 14:03
import logging

from pydantic import BaseModel, Field

from flask_openapi3 import FileStorage, OpenAPI


logger = logging.getLogger(__name__)

app = OpenAPI(__name__)


class UploadFileForm(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="File Type")


class UploadFilesForm(BaseModel):
    files: list[FileStorage]
    str_list: list[str]
    int_list: list[int]


@app.post("/upload/file")
def upload_file(form: UploadFileForm):
    logger.info(form.file.filename)
    logger.info(form.file_type)
    form.file.save("test.jpg")
    return {"code": 0, "message": "ok"}


@app.post("/upload/files")
def upload_files(form: UploadFilesForm):
    logger.info(form.files)
    logger.info(form.str_list)
    logger.info(form.int_list)
    return {"code": 0, "message": "ok"}


if __name__ == "__main__":
    app.run(debug=True)  # nosec
