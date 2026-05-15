from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Client
from enamelware.schemas import ClientCreate, ClientOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=dict)
def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    query = db.query(Client)
    if search:
        query = query.filter(Client.name.ilike(f"%{search}%"))
    total = query.count()
    clients = query.order_by(Client.name).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [ClientOut.model_validate(c) for c in clients]}


@router.get("/all", response_model=list[ClientOut])
def list_all_clients(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    return db.query(Client).filter(Client.is_active == True).all()


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Client not found"})
    return c


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(data: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    existing = db.query(Client).filter(Client.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Client already exists"})
    c = Client(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{client_id}", response_model=ClientOut)
def update_client(client_id: int, data: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Client not found"})
    existing = db.query(Client).filter(Client.name == data.name, Client.id != client_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Client name already exists"})
    for key, value in data.model_dump().items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Client not found"})
    from enamelware.models import Sale
    if db.query(Sale).filter(Sale.client_id == client_id).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_references", "message": "Cannot delete client with sales"})
    db.delete(c)
    db.commit()
    return {"message": "Client deleted"}