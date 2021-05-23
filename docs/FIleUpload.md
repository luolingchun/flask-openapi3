```python
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, FileStorage

app = OpenAPI(__name__)


class UploadFile(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="文件类型")


@app.post('/upload')
def upload_file(form: UploadFile):
    print(form.file.filename)
    print(form.file_type)
    form.file.save('test.jpg')
    return {"code": 0, "message": "ok"}


if __name__ == '__main__':
    app.run(debug=True)
```

