from typing import List
from fastapi import APIRouter
from uuid import UUID

from app.models.knowledge_graph import KnowledgeGraphRead, KnowledgeGraphCreate
from app.services.knowledge_graph_management import KnowledgeGraphManagement

router = APIRouter(
    prefix="/management",
    tags=["management"]
)

knowledgeGraphManagement = KnowledgeGraphManagement()

@router.get("/", response_model=List[KnowledgeGraphRead], status_code=200)
async def get_all_knowledge_graphs():
    return knowledgeGraphManagement.get_all()


@router.get("/{id}", response_model=KnowledgeGraphRead, status_code=200)
async def get_knowledge_graph_by_id(id: UUID):
    return knowledgeGraphManagement.get_by_id(id)


@router.post("/", response_model=KnowledgeGraphRead, status_code=201)
async def start_knowledge_graph_versioning(knowledgeGraph: KnowledgeGraphCreate):
    return knowledgeGraphManagement.add(knowledgeGraph)

@router.delete("/{id}", status_code=200)
async def stop_knowledge_graph_versioning_by_id(id: UUID):
    return knowledgeGraphManagement.delete(id)
