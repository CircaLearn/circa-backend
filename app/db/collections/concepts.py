def fetch_concepts(db):
    concepts_collection = db.concepts
    return list(concepts_collection.find())
