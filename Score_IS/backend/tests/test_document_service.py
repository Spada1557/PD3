"""Тесты бизнес-логики проведения и отмены закупок и продаж."""
import pytest
from app import models, crud
from app.services import document_service as svc


def make_purchase(db, supplier, user, items):
    number = svc.generate_number(db, "ПУ")
    purchase = models.Purchase(
        number=number,
        supplier_id=supplier.id,
        created_by=user.id,
        status=models.DocumentStatus.draft,
    )
    db.add(purchase)
    db.flush()
    total = 0.0
    for product, qty, price in items:
        amount = qty * price
        total += amount
        db.add(models.PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            quantity=qty,
            price=price,
            amount=amount,
        ))
    purchase.total_amount = total
    db.commit()
    db.refresh(purchase)
    return purchase


def make_sale(db, client, user, items_stock):
    """items_stock: list of (product, qty, price) — qty должна быть <= stock.quantity."""
    number = svc.generate_number(db, "ПР")
    sale = models.Sale(
        number=number,
        client_id=client.id,
        created_by=user.id,
        status=models.DocumentStatus.draft,
    )
    db.add(sale)
    db.flush()
    total = 0.0
    for product, qty, price in items_stock:
        amount = qty * price
        total += amount
        db.add(models.SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            quantity=qty,
            price=price,
            amount=amount,
        ))
    sale.total_amount = total
    db.commit()
    db.refresh(sale)
    return sale


# ─── Вспомогательные фикстуры ────────────────────────────────────────────────

@pytest.fixture
def supplier(seeded_db):
    db = seeded_db["db"]
    s = models.Supplier(name="ООО Тест", inn="1234567890")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def client_obj(seeded_db):
    db = seeded_db["db"]
    c = models.Client(name="Клиент Тест", inn="0987654321")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ─── Тесты закупки ───────────────────────────────────────────────────────────

class TestPostPurchase:
    def test_stock_increases(self, seeded_db, supplier):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        purchase = make_purchase(db, supplier, user, [(product, 10, 150.0)])
        svc.post_purchase(db, purchase, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 10.0

    def test_avg_cost_calculated(self, seeded_db, supplier):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        # Первая партия 10 шт по 100
        p1 = make_purchase(db, supplier, user, [(product, 10, 100.0)])
        svc.post_purchase(db, p1, user.id)
        # Вторая партия 10 шт по 200
        p2 = make_purchase(db, supplier, user, [(product, 10, 200.0)])
        svc.post_purchase(db, p2, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 20.0
        assert stock.avg_cost == 150.0  # (100*10 + 200*10) / 20

    def test_double_post_raises(self, seeded_db, supplier):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        purchase = make_purchase(db, supplier, user, [(product, 5, 100.0)])
        svc.post_purchase(db, purchase, user.id)
        with pytest.raises(ValueError, match="уже проведен"):
            svc.post_purchase(db, purchase, user.id)

    def test_status_becomes_posted(self, seeded_db, supplier):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        purchase = make_purchase(db, supplier, user, [(product, 5, 100.0)])
        svc.post_purchase(db, purchase, user.id)
        assert purchase.status == models.DocumentStatus.posted


class TestCancelPurchase:
    def test_stock_decreases(self, seeded_db, supplier):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        purchase = make_purchase(db, supplier, user, [(product, 10, 150.0)])
        svc.post_purchase(db, purchase, user.id)
        svc.cancel_purchase(db, purchase, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 0.0

    def test_avg_cost_restored(self, seeded_db, supplier):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        # Первая партия 10 по 100 → avg=100
        p1 = make_purchase(db, supplier, user, [(product, 10, 100.0)])
        svc.post_purchase(db, p1, user.id)
        # Вторая партия 10 по 200 → avg=150
        p2 = make_purchase(db, supplier, user, [(product, 10, 200.0)])
        svc.post_purchase(db, p2, user.id)
        # Отмена второй → должна вернуть avg=100
        svc.cancel_purchase(db, p2, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 10.0
        assert stock.avg_cost == 100.0

    def test_cancel_unposted_raises(self, seeded_db, supplier):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        purchase = make_purchase(db, supplier, user, [(product, 5, 100.0)])
        with pytest.raises(ValueError, match="не проведен"):
            svc.cancel_purchase(db, purchase, user.id)

    def test_insufficient_stock_raises(self, seeded_db, supplier):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        purchase = make_purchase(db, supplier, user, [(product, 10, 100.0)])
        svc.post_purchase(db, purchase, user.id)
        # Вручную опустим остаток ниже количества в закупке
        stock = crud.get_stock_item(db, product.id, warehouse.id)
        stock.quantity = 5.0
        db.commit()
        with pytest.raises(ValueError, match="Недостаточно остатка"):
            svc.cancel_purchase(db, purchase, user.id)


# ─── Тесты продажи ───────────────────────────────────────────────────────────

class TestPostSale:
    def _prepare_stock(self, db, user, product, supplier, qty=20, price=100.0):
        purchase = make_purchase(db, supplier, user, [(product, qty, price)])
        svc.post_purchase(db, purchase, user.id)

    def test_stock_decreases(self, seeded_db, supplier, client_obj):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        self._prepare_stock(db, user, product, supplier, qty=20, price=100.0)
        sale = make_sale(db, client_obj, user, [(product, 5, 500.0)])
        svc.post_sale(db, sale, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 15.0

    def test_cost_calculated_from_avg(self, seeded_db, supplier, client_obj):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        self._prepare_stock(db, user, product, supplier, qty=10, price=100.0)
        sale = make_sale(db, client_obj, user, [(product, 3, 500.0)])
        svc.post_sale(db, sale, user.id)

        assert sale.total_cost == 300.0  # 3 * avg_cost(100)
        item = sale.items[0]
        assert item.cost == 300.0

    def test_no_stock_raises(self, seeded_db, client_obj):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        sale = make_sale(db, client_obj, user, [(product, 1, 500.0)])
        with pytest.raises(ValueError, match="отсутствует на складе"):
            svc.post_sale(db, sale, user.id)

    def test_insufficient_stock_raises(self, seeded_db, supplier, client_obj):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        self._prepare_stock(db, user, product, supplier, qty=5, price=100.0)
        sale = make_sale(db, client_obj, user, [(product, 10, 500.0)])
        with pytest.raises(ValueError, match="Недостаточно остатка"):
            svc.post_sale(db, sale, user.id)


class TestCancelSale:
    def _prepare_sale(self, db, user, product, supplier, client_obj):
        purchase = make_purchase(db, supplier, user, [(product, 20, 100.0)])
        svc.post_purchase(db, purchase, user.id)
        sale = make_sale(db, client_obj, user, [(product, 5, 500.0)])
        svc.post_sale(db, sale, user.id)
        return sale

    def test_stock_restored(self, seeded_db, supplier, client_obj):
        db, user, product, warehouse = (
            seeded_db["db"], seeded_db["user"],
            seeded_db["product"], seeded_db["warehouse"],
        )
        sale = self._prepare_sale(db, user, product, supplier, client_obj)
        svc.cancel_sale(db, sale, user.id)

        stock = crud.get_stock_item(db, product.id, warehouse.id)
        assert stock.quantity == 20.0  # 20 - 5 + 5

    def test_cancel_unposted_raises(self, seeded_db, client_obj):
        db, user, product = seeded_db["db"], seeded_db["user"], seeded_db["product"]
        sale = make_sale(db, client_obj, user, [(product, 1, 500.0)])
        with pytest.raises(ValueError, match="не проведен"):
            svc.cancel_sale(db, sale, user.id)
