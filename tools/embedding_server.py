from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import uvicorn
from typing import Union

app = FastAPI()

# Load a multilingual model good for Korean
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
print(f"Loading model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print(f"Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")

class EmbRequest(BaseModel):
    input: Union[str, list[str]]
    model: str = MODEL_NAME

@app.get("/")
async def root():
    return {"status": "ok", "model": MODEL_NAME, "dimension": model.get_sentence_embedding_dimension()}

@app.post("/v1/embeddings")
async def embeddings(req: EmbRequest):
    try:
        # Handle both single string and list of strings
        texts = [req.input] if isinstance(req.input, str) else req.input

        vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

        # OpenAI-compatible response format
        return {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": vec.tolist(),
                    "index": i
                }
                for i, vec in enumerate(vectors)
            ],
            "model": MODEL_NAME,
            "usage": {
                "prompt_tokens": sum(len(t.split()) for t in texts),
                "total_tokens": sum(len(t.split()) for t in texts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting local embedding server on http://127.0.0.1:8001")
    print("Press CTRL+C to quit")
    uvicorn.run(app, host="127.0.0.1", port=8001)
