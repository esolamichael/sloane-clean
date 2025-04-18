from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "AI Phone Answering Service Test",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test():
    return {"message": "API is working!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

