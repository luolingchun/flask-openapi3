# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/11 14:03

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, FileStorage

app = OpenAPI(__name__)


class UploadFileForm(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="File Type")


@app.post('/upload')
def upload_file(form: UploadFileForm):
    print(form.file.filename)
    print(form.file_type)
    form.file.save('test.jpg')
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
