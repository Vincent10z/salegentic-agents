# router.py
from fastapi import APIRouter
from app.api.routes.v1.workspace import endpoints
from .response import WorkspaceResponse, WorkspacesListResponse, WorkspaceDeleteResponse, ErrorResponse

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspace"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

router.add_api_route(
    path="",
    endpoint=endpoints.create_workspace,
    methods=["POST"],
    summary="Create a new workspace",
    description="Create a new workspace in the system",
    response_model=WorkspaceResponse,
    status_code=201,
)

router.add_api_route(
    path="",
    endpoint=endpoints.list_workspaces,
    methods=["GET"],
    summary="List workspaces",
    description="Get a paginated list of workspaces",
    response_model=WorkspacesListResponse,
    status_code=200,
)

router.add_api_route(
    path="/{workspace_id}",
    endpoint=endpoints.get_workspace,
    methods=["GET"],
    summary="Get a specific workspace",
    description="Get details of a specific workspace",
    response_model=WorkspaceResponse,
    status_code=200,
)

router.add_api_route(
    path="/{workspace_id}",
    endpoint=endpoints.update_workspace,
    methods=["PUT"],
    summary="Update a specific workspace",
    description="Update details of a specific workspace",
    response_model=WorkspaceResponse,
    status_code=200,
)

router.add_api_route(
    path="/{workspace_id}",
    endpoint=endpoints.delete_workspace,
    methods=["DELETE"],
    summary="Delete a specific workspace",
    description="Delete a specific workspace",
    response_model=WorkspaceDeleteResponse,
    status_code=200,
)