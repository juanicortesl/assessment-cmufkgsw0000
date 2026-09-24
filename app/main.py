from fastapi import FastAPI
from app.db import Base, engine
from app.routers import documents

# Inicializar tablas de esquema en base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Total Abogados - Document Rendering Service")

app.include_router(documents.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
