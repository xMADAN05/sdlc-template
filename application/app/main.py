import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import v1_router
from core.session_manager import session_manager
from utils.common_utils import openapi_spec

logger = logging.getLogger(__name__)

logger.info("Application starting")

sdlc_test_backend = FastAPI(
    title="Test Case Generator API",
    description="API for generating structured test cases in JSON format",
    version="0.0.3"
)


sdlc_test_backend.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if openapi_spec:
#     sdlc_test_backend.openapi_schema = openapi_spec
    


@sdlc_test_backend.get("/healthcheck", tags=["healthcheck"])
def get_healthcheck_response():
    # Clean up inactive sessions
    session_manager.remove_inactive_sessions()
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "active_sessions": session_manager.count_active_sessions()
    }

sdlc_test_backend.include_router(v1_router, prefix= '/v1/sdlc-test-gen')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(sdlc_test_backend, host="0.0.0.0", port=8002)