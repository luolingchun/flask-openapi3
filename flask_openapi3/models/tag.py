from pydantic import BaseModel

from .external_documentation import ExternalDocumentation


class Tag(BaseModel):
    """
    https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#tag-object
    """

    name: str
    description: str | None = None
    externalDocs: ExternalDocumentation | None = None

    model_config = {"extra": "allow"}
