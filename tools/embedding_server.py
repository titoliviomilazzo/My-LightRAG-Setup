from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
import uvicorn

app = FastAPI()

# Load a multilingual model good for Korean
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
model = SentenceTransformer(MODEL_NAME)

class EmbRequest(BaseModel):
    input: list[str]

@app.post("/v1/embeddings")
async def embeddings(req: EmbRequest):
    try:
        vectors = model.encode(req.input, show_progress_bar=False, convert_to_numpy=True)
        return {"data": [{"embedding": vec.tolist()} for vec in vectors]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
