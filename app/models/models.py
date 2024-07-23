from pydantic import BaseModel, Field, computed_field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from app.helpers.similarity import calculate_normalized_embeddings
from datetime import datetime
from bson import ObjectId
from typing import Optional, Annotated, List


# Custom type for ObjectId, represented as a string in the model for JSON
# serialization
PyObjectId = Annotated[str, BeforeValidator(str)]

class ConceptModel(BaseModel):
    """
    Container for a single concept record.
    """
    id: PyObjectId = Field(alias="_id", default_factory=ObjectId)
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
        return calculate_normalized_embeddings(embed_string)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "80b9d6e1e1b8f30d6c8e6f59",
                "user_id": "60b8d6e1e1b8f30d6c8e6f59",
                "name": "Example Concept",
                "usage": "How you use it",
                "date_created": "2023-07-23T10:00:00Z",
                "last_seen": "2023-07-23T12:00:00Z",
                "progress": 0.5,
                "normalized_embedding": [0.1, 0.2, 0.3, ...],
            }
        },
    )


# run as a module: python3 -m app.models.models
instance = ConceptModel(user_id="60b8d6e1e1b8f30d6c8e6f59",
                        name = "Test",
                        usage="also test")

print(instance.normalized_embedding)
