from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case table name
        name = cls.__name__
        result = [name[0].lower()]
        for char in name[1:]:
            if char.isupper():
                result.append("_")
                result.append(char.lower())
            else:
                result.append(char)
        
        # Pluralize table name
        tablename = "".join(result)
        if tablename.endswith("y"):
            return tablename[:-1] + "ies"
        elif not tablename.endswith("s"):
            return tablename + "s"
        return tablename
