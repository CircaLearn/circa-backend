from pydantic import BaseModel, Field, computed_field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from app.helpers.similarity import calculate_normalized_embeddings, tensor_to_list
from datetime import datetime
from typing import Optional, Annotated, List
from bson import ObjectId


# Custom type for ObjectId, represented as a string in the model for JSON
# serialization
PyObjectId = Annotated[str, BeforeValidator(str)]

class ConceptModel(BaseModel):
    """
    Container for a single concept record.
    """
    # Best practice to let MongoDB handle _id generation, so we default to None
    # Alias is what is used for serialization & deserialization, but internally
    # we can refer to _id or id
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    name: str  # Required field
    usage: str  # Required field
    date_created: Annotated[datetime, Field(default_factory=datetime.now)]
    last_seen: Optional[datetime] = None
    progress: Annotated[float, Field(default=0, ge=0, le=1)]

    @computed_field
    def normalized_embedding(self) -> List[float]:
        # Compute the normalized embedding based on name and usage
        embed_string = f"{self.name}: {self.usage}"
        return tensor_to_list(calculate_normalized_embeddings(embed_string))

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "80b9d6e1e1b8f30d6c8e6f59",
                "user_id": "60b8d6e1e1b8f30d6c8e6f59",
                "name": "Example Concept",
                "usage": "This is how you use it",
                "date_created": "2023-07-23T10:00:00Z",
                "progress": 0.0,
            }
        },
    )


class UpdateConceptModel(BaseModel):
    """
    Model for possible updates to an existing concept.

    Only name and usage can be modified (embedding is updated automatically)
    """
    name: Optional[str] = None
    usage: Optional[str] = None
    last_seen: Optional[datetime] = None


class UserModel(BaseModel):
    """
    Container for a single user record
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str # unique, validate in API routes
    username: str
    password: str
    profile_picture: Optional[str] = None 
    date_created: Annotated[datetime, Field(default_factory=datetime.now)]
    last_seen: Annotated[datetime, Field(default_factory=datetime.now)]
    day_streak: Annotated[int, Field(default=0)]

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": { # data used as default in /docs users POST
                "email": "test@tester.com",
                "username": "TestyTest",
                "password": "password123",
            }
        },
    )


class UpdateUserModel(BaseModel):
    """
    Model for possible updates to an existing user. 
    
    Only usernames, passwords and profile_pictures may be updated.
    """
    username: Optional[str] = None
    password: Optional[str] = None
    profile_picture: Optional[str] = None


if __name__ == '__main__':
    # run as a module: python3 -m app.models.models
    instance = ConceptModel(user_id="60b8d6e1e1b8f30d6c8e6f59",
                            name = "Test",
                            usage="also test")

    print(instance.normalized_embedding)
