from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI AdTech RAG Platform",
        version="0.1.0",
        description="AI-powered ad campaign insights + RAG + explainable recs.",
    )

    # This is the glue layer: CORS + routing + whatever middleware we add later.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    return app


app = create_app()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
