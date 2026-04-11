from fastapi import FastAPI, Request
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
from app.db.engine import Base, engine

# from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time


from app.routers.auth_routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    simple function for run and stop app
    """

    print("""

        ******************  start app successfully  ******************
        
        """)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("""

        ******************  app was shutdown   ******************
    
    """)


tags_metadata = [
    {"name": "auth", "description": "all authentication operation"},
    {"name": "users", "description": "all users operation"},
    {"name": "teams", "description": "all teams operation"},
    {"name": "projects", "description": "all projects operation"},
    {"name": "tasks", "description": "all tasks operation"},
    {"name": "auth", "description": "all authentication operation"},
]

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None,
    title="MINI_SAAS_TASKFLOW",
    description="this is a simple tasks manager for any team",
    summary="use for manage team, task, user, and something else",
    version="0.1.0",
    terms_of_service="http://www.nadarimfelan.ir",
    contact={
        "name": "Mohammad Mahdi Hassanzadeh",
        "url": "http://github.com/Thehassanzadeh/",
        "email": "mohammad.hassanzadehh@gmail.com",
    },
    license_info={"name": "MIT"},
    openapi_url="/api/v1/",
    openapi_tags=tags_metadata,
)

patch_fastapi(app, docs_url="/swagger")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"             process time:{process_time: .2f}ms")
    return response


app.add_middleware(GZipMiddleware, minimum_size=1000)


app.include_router(auth_router)
