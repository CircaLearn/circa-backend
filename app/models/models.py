from pydantic import BaseModel, Field, computed_field
from app.helpers.similarity import calculate_normalized_embeddings
# from bson import ObjectId
from typing import Optional


# class Concept(BaseModel):
#     user_id: ObjectId = Field(default_factory=ObjectId, alias="_id")
#     name: constr(strip_whitespace=True) = Field(..., description="Name of the concept")
#     usage: constr(strip_whitespace=True) = Field(
#         ..., description="Usage of the concept"
#     )
#     date_created: datetime = Field(default_factory=datetime.utcnow)
#     last_seen: Optional[datetime] = None
#     progress: conint(ge=0, le=1) = Field(default=0)

#     @computed_field
#     def normalized_embedding(self) -> list[float]:
#         # including name in embedding -- TODO play around for best performance
#         embed_string = self.name + ": " + self.usage
#         return calculate_normalized_embeddings(embed_string)
