import random
import string
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api import management_rest_service, query_rest_service
from app.database import create_db_and_tables
from app.services.knowledge_graph_management import KnowledgeGraphNotFoundException

import logging

LOG = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # optional action after terminatin application here

app = FastAPI(lifespan=lifespan)

app.include_router(management_rest_service.router);
app.include_router(query_rest_service.router);


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    LOG.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    LOG.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
    return response

@app.exception_handler(KnowledgeGraphNotFoundException)
async def knowledge_graph_not_found_exception_handler(request: Request, exc: KnowledgeGraphNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Oops! Knowledge Graph with id {exc.id} not found!"},
    )