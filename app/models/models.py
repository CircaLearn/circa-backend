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
    # best practice to let mongodb handle _id generation, so we default to None
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # 3 dots is pydantic/fastapi notation for being required
    user_id: PyObjectId = Field(...)
    name: Annotated[str, Field(...)]
    usage: Annotated[str, Field(...)]
    date_created: Annotated[datetime, Field(default_factory=datetime.now)]
    last_seen: Optional[datetime] = None
    progress: Annotated[float, Field(default=0, ge=0, le=1)]

    @computed_field
    def normalized_embedding(self) -> List[float]:
        # Compute the normalized embedding based on name and usage
        embed_string = f"{self.name}: {self.usage}"
        return tensor_to_list(calculate_normalized_embeddings(embed_string))
        
    model_config = ConfigDict(
        json_encoders = {
            ObjectId: str,
        },
        populate_by_name=True,
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


if __name__ == '__main__':
    # run as a module: python3 -m app.models.models
    instance = ConceptModel(user_id="60b8d6e1e1b8f30d6c8e6f59",
                            name = "Test",
                            usage="also test")

    print(instance.normalized_embedding)
