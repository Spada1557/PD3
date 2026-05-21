from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app import crud, schemas, models

router = APIRouter(prefix="/references", tags=["References"])

# Categories
@router.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.post("/categories", response_model=schemas.CategoryOut)
def create_category(obj: schemas.CategoryCreate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager", "warehouse"]))):
    return crud.create_category(db, obj)

# Units
@router.get("/units", response_model=list[schemas.UnitOut])
def list_units(db: Session = Depends(get_db)):
    return crud.get_units(db)

@router.post("/units", response_model=schemas.UnitOut)
def create_unit(obj: schemas.UnitCreate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager", "warehouse"]))):
    return crud.create_unit(db, obj)

# Warehouses
@router.get("/warehouses", response_model=list[schemas.WarehouseOut])
def list_warehouses(db: Session = Depends(get_db)):
    return crud.get_warehouses(db)

@router.post("/warehouses", response_model=schemas.WarehouseOut)
def create_warehouse(obj: schemas.WarehouseCreate, db: Session = Depends(get_db), user: models.User = Depends(require_role("admin"))):
    return crud.create_warehouse(db, obj)

# Suppliers
@router.get("/suppliers", response_model=schemas.PaginatedResponse)
def list_suppliers(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=5000), search: str | None = None, db: Session = Depends(get_db)):
    result = crud.get_suppliers(db, page=page, per_page=per_page, search=search)
    return jsonable_encoder(result)

@router.post("/suppliers", response_model=schemas.SupplierOut)
def create_supplier(obj: schemas.SupplierCreate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "warehouse"]))):
    return crud.create_supplier(db, obj)

@router.get("/suppliers/{supplier_id}", response_model=schemas.SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    s = crud.get_supplier(db, supplier_id)  # нужно добавить
    if not s:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return s

@router.put("/suppliers/{supplier_id}", response_model=schemas.SupplierOut)
def update_supplier(supplier_id: int, obj: schemas.SupplierUpdate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "warehouse"]))):
    db_obj = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return crud.update_supplier(db, db_obj, obj)

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "warehouse"]))):
    db_obj = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    crud.delete_supplier(db, db_obj)
    return {"detail": "Удалено"}

# Clients
@router.get("/clients", response_model=schemas.PaginatedResponse)
def list_clients(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=5000), search: str | None = None, db: Session = Depends(get_db)):
    result = crud.get_clients(db, page=page, per_page=per_page, search=search)
    return jsonable_encoder(result)

@router.post("/clients", response_model=schemas.ClientOut)
def create_client(obj: schemas.ClientCreate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager"]))):
    return crud.create_client(db, obj)

@router.get("/clients/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return c

@router.put("/clients/{client_id}", response_model=schemas.ClientOut)
def update_client(client_id: int, obj: schemas.ClientUpdate, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager"]))):
    db_obj = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return crud.update_client(db, db_obj, obj)

@router.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager"]))):
    db_obj = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    crud.delete_client(db, db_obj)
    return {"detail": "Удалено"}
