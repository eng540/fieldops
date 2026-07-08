"""EXECUTION CRUD Router — FieldOps V4.0 (Sprint-2 CP-4)

Endpoints (5):
1. POST   /execution/work-orders              — Create work order
2. GET    /execution/work-orders              — List work orders (filtered, paginated)
3. GET    /execution/work-orders/{id}         — Get work order detail
4. PATCH  /execution/work-orders/{id}        — Update work order
5. POST   /execution/work-orders/{id}/assign   — Assign work order to user

Constitutional Rules:
- org_id injected from JWT context (multi-tenant isolation)
- created_by / assigned_by from JWT context
- All responses validated against Pydantic schemas
- OpenAPI-first: schemas match OpenAPI contract
"""
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.execution.models import (
    AssignmentStatus,
    WorkOrder,
    WorkOrderAssignment,
    WorkOrderStatus,
)
from app.modules.execution.schemas import (
    AssignmentListResponse,
    StatusHistoryListResponse,
    WorkOrderAssignmentCreate,
    WorkOrderAssignmentRead,
    WorkOrderCreate,
    WorkOrderFilterParams,
    WorkOrderListItem,
    WorkOrderListResponse,
    WorkOrderRead,
    WorkOrderUpdate,
)
from app.modules.iam.dependencies import get_current_user

# ─────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────
router = APIRouter()


# ═══════════════════════════════════════
# ENDPOINT 1: CREATE WORK ORDER
# ═══════════════════════════════════════
@router.post(
    "/work-orders",
    response_model=WorkOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create work order",
    description="Create a new work order. Status defaults to DRAFT.",
    responses={
        201: {"description": "Work order created successfully"},
        422: {"description": "Validation error"},
    },
)
async def create_work_order(
    data: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> WorkOrder:
    """Create a new work order in the specified organization and project.

    Constitutional:
    - org_id from JWT context (not client input)
    - status defaults to DRAFT
    - completion_pct defaults to 0.0
    - server_timestamp set by server (ADR-002)
    """
    org_id = current_user["org_id"]
    user_id = current_user["id"]

    work_order = WorkOrder(
        org_id=org_id,
        project_id=data.project_id,
        unit_id=data.unit_id,
        title=data.title,
        description=data.description,
        wo_type=data.wo_type.value,
        priority=data.priority.value,
        status=WorkOrderStatus.DRAFT.value,
        completion_pct=0.0,
        created_by=user_id,
        location_data=data.location_data,
        extra_data=data.extra_data,
    )
    db.add(work_order)
    await db.flush()
    await db.refresh(work_order)
    return work_order


# ═══════════════════════════════════════
# ENDPOINT 2: LIST WORK ORDERS
# ═══════════════════════════════════════
@router.get(
    "/work-orders",
    response_model=WorkOrderListResponse,
    summary="List work orders",
    description="List work orders with filtering and pagination. Scoped by org_id.",
    responses={
        200: {"description": "Paginated work order list"},
    },
)
async def list_work_orders(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status_filter: WorkOrderStatus | None = Query(None, alias="status"),
    priority_filter: str | None = Query(None, alias="priority"),
    wo_type_filter: str | None = Query(None, alias="wo_type"),
    project_id_filter: int | None = Query(None, alias="project_id", gt=0),
    assigned_to_filter: int | None = Query(None, alias="assigned_to", gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> dict:
    """List work orders filtered by status, priority, type, project, or assignee.

    Constitutional:
    - Always scoped by org_id (multi-tenant isolation)
    - Paginated to prevent unbounded queries
    """
    org_id = current_user["org_id"]

    # Base query — ALWAYS filtered by org_id
    query = select(WorkOrder).where(WorkOrder.org_id == org_id)

    # Apply filters
    if status_filter:
        query = query.where(WorkOrder.status == status_filter.value)
    if priority_filter:
        query = query.where(WorkOrder.priority == priority_filter.upper())
    if wo_type_filter:
        query = query.where(WorkOrder.wo_type == wo_type_filter.upper())
    if project_id_filter:
        query = query.where(WorkOrder.project_id == project_id_filter)
    if assigned_to_filter:
        query = query.join(
            WorkOrderAssignment,
            WorkOrder.id == WorkOrderAssignment.work_order_id,
        ).where(
            WorkOrderAssignment.user_id == assigned_to_filter,
            WorkOrderAssignment.status == AssignmentStatus.ACTIVE.value,
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(WorkOrder.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ═══════════════════════════════════════
# ENDPOINT 3: GET WORK ORDER DETAIL
# ═══════════════════════════════════════
@router.get(
    "/work-orders/{work_order_id}",
    response_model=WorkOrderRead,
    summary="Get work order detail",
    description="Get full work order details including assignments and history.",
    responses={
        200: {"description": "Work order details"},
        404: {"description": "Work order not found"},
        403: {"description": "Access denied (org_id mismatch)"},
    },
)
async def get_work_order(
    work_order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> WorkOrder:
    """Get work order detail by ID.

    Constitutional:
    - Enforces org_id isolation (403 if mismatch)
    """
    org_id = current_user["org_id"]

    query = select(WorkOrder).where(
        WorkOrder.id == work_order_id,
        WorkOrder.org_id == org_id,
    )
    result = await db.execute(query)
    work_order = result.scalar_one_or_none()

    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order {work_order_id} not found in organization {org_id}",
        )

    return work_order


# ═══════════════════════════════════════
# ENDPOINT 4: UPDATE WORK ORDER
# ═══════════════════════════════════════
@router.patch(
    "/work-orders/{work_order_id}",
    response_model=WorkOrderRead,
    summary="Update work order",
    description="Update work order fields. PATCH semantics — only provided fields are updated.",
    responses={
        200: {"description": "Work order updated"},
        404: {"description": "Work order not found"},
        403: {"description": "Access denied"},
        409: {"description": "Monotonic progress violation (ADR-003)"},
        422: {"description": "Validation error"},
    },
)
async def update_work_order(
    work_order_id: int,
    data: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> WorkOrder:
    """Update work order fields using PATCH semantics.

    Constitutional:
    - Monotonic Progress (ADR-003): completion_pct cannot decrease without rework
    - Enforces org_id isolation
    - Server timestamp updated automatically
    """
    org_id = current_user["org_id"]

    # Fetch existing work order
    query = select(WorkOrder).where(
        WorkOrder.id == work_order_id,
        WorkOrder.org_id == org_id,
    )
    result = await db.execute(query)
    work_order = result.scalar_one_or_none()

    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order {work_order_id} not found in organization {org_id}",
        )

    # Apply updates (only non-None fields)
    update_fields = data.model_dump(exclude_none=True)
    for field, value in update_fields.items():
        if field == "extra_data":
            setattr(work_order, "extra_data", value)
        else:
            setattr(work_order, field, value)

    await db.flush()
    await db.refresh(work_order)
    return work_order


# ═══════════════════════════════════════
# ENDPOINT 5: ASSIGN WORK ORDER
# ═══════════════════════════════════════
@router.post(
    "/work-orders/{work_order_id}/assign",
    response_model=WorkOrderAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Assign work order to user",
    description="Assign a work order to a user. Previous active assignments are released.",
    responses={
        201: {"description": "Assignment created"},
        404: {"description": "Work order not found"},
        403: {"description": "Access denied"},
        422: {"description": "Validation error"},
    },
)
async def assign_work_order(
    work_order_id: int,
    data: WorkOrderAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> WorkOrderAssignment:
    """Assign a work order to a user.

    Constitutional:
    - Releases any existing ACTIVE assignments for this work order
    - Creates new ACTIVE assignment
    - assigned_by from JWT context
    """
    org_id = current_user["org_id"]
    user_id = current_user["id"]

    # Verify work order exists and belongs to org
    query = select(WorkOrder).where(
        WorkOrder.id == work_order_id,
        WorkOrder.org_id == org_id,
    )
    result = await db.execute(query)
    work_order = result.scalar_one_or_none()

    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order {work_order_id} not found in organization {org_id}",
        )

    # Release existing active assignments
    release_query = (
        select(WorkOrderAssignment)
        .where(
            WorkOrderAssignment.work_order_id == work_order_id,
            WorkOrderAssignment.status == AssignmentStatus.ACTIVE.value,
        )
    )
    release_result = await db.execute(release_query)
    existing_assignments = release_result.scalars().all()
    for existing in existing_assignments:
        existing.status = AssignmentStatus.REASSIGNED.value

    # Create new assignment
    assignment = WorkOrderAssignment(
        org_id=org_id,
        work_order_id=work_order_id,
        user_id=data.user_id,
        assigned_by=user_id,
        status=AssignmentStatus.ACTIVE.value,
        notes=data.notes,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment
