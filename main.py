from app import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    port = 8001
    uvicorn.run(app="main:app", host="0.0.0.0", port=port,reload=True)
