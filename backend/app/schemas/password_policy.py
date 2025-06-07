from pydantic import BaseModel

class PasswordPolicyRead(BaseModel):
    id: int | None = None
    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_symbols: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_symbols": True,
            }
        }

class PasswordPolicyUpdate(BaseModel):
    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_symbols: bool
