from typing import Annotated
from pydantic import (
    EmailStr,
    Field,
)

str_128 = Annotated[str, Field(min_length=1, max_length=128)]
str_512 = Annotated[str, Field(min_length=1, max_length=512)]
email_str = Annotated[EmailStr, Field(min_length=1, max_length=128)]
int_positive = Annotated[int, Field(ge=1)]
str_positive = Annotated[str, Field(min_length=1)]
