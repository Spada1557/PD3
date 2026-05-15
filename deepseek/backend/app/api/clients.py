from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client
from app.schemas import ClientCreate, ClientUpdate, ClientResponse, PaginatedResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


@router.get("", response_model=PaginatedResponse)
def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    from sqlalchemy import or_
    q = db.query(Client)
    if search:
        q = q.filter(or_(Client.name.ilike(f"%{search}%"), Client.inn.ilike(f"%{search}%")))
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[ClientResponse.model_validate(c) for c in items])


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Клиент не найден"})
    return c


@router.post("", response_model=ClientResponse, status_code=201)
def create_client(body: ClientCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = Client(**body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, body: ClientUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Клиент не найден"})
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Клиент не найден"})
    c.status = "inactive"
    db.commit()
    return {"message": "Клиент деактивирован"}
