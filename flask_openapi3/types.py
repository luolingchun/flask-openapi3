from typing import Optional, Dict, Type

from pydantic import BaseModel


OpenAPIResponsesType = Optional[Dict[str, Optional[Type[BaseModel]]]]
