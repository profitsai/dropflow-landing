import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


def _derive_fernet_key(raw_value: str) -> bytes:
    """
    Build a valid Fernet key from an env-provided value.

    - If raw_value is already a valid Fernet key, use it directly.
    - Otherwise derive one deterministically via SHA-256.
    """
    try:
        Fernet(raw_value.encode("utf-8"))
        return raw_value.encode("utf-8")
    except Exception:
        digest = hashlib.sha256(raw_value.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


def _get_vault_cipher() -> Fernet:
    """Return the Fernet cipher for SupplierVault encryption.

    CRITICAL: We require VAULT_ENCRYPTION_KEY explicitly.
    Falling back to SECRET_KEY couples session security to vault encryption and
    makes key rotation dangerous (it would silently break decryption).
    """
    key_source = os.getenv("VAULT_ENCRYPTION_KEY")
    if not key_source:
        raise RuntimeError(
            "Missing VAULT_ENCRYPTION_KEY. Generate a Fernet key and set it in your environment/.env"
        )
    return Fernet(_derive_fernet_key(key_source))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    ebay_stores = db.relationship("EbayStore", back_populates="user", cascade="all, delete-orphan")
    supplier_vaults = db.relationship("SupplierVault", back_populates="user", cascade="all, delete-orphan")
    products = db.relationship("Product", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, plain_password: str) -> None:
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.password_hash, plain_password)


class EbayStore(db.Model):
    __tablename__ = "ebay_stores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    store_name = db.Column(db.String(120), nullable=True)
    ebay_username = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="ebay_stores")
    products = db.relationship("Product", back_populates="ebay_store", cascade="all, delete-orphan")


class SupplierVault(db.Model):
    __tablename__ = "supplier_vaults"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    supplier_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    encrypted_password = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="supplier_vaults")

    def set_password(self, plain_password: str) -> None:
        cipher = _get_vault_cipher()
        self.encrypted_password = cipher.encrypt(plain_password.encode("utf-8")).decode("utf-8")

    def get_password(self) -> str | None:
        if not self.encrypted_password:
            return None

        cipher = _get_vault_cipher()
        try:
            return cipher.decrypt(self.encrypted_password.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Could not decrypt SupplierVault password with current key") from exc


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    ebay_store_id = db.Column(db.Integer, db.ForeignKey("ebay_stores.id"), nullable=False, index=True)
    source_url = db.Column(db.Text, nullable=True)
    source_sku = db.Column(db.String(120), nullable=True)
    ebay_item_id = db.Column(db.String(120), nullable=True)
    title = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(30), nullable=False, server_default="draft")
    source_cost = db.Column(db.Numeric(10, 2), nullable=True)
    target_price = db.Column(db.Numeric(10, 2), nullable=True)
    last_synced_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="products")
    ebay_store = db.relationship("EbayStore", back_populates="products")
    orders = db.relationship("Order", back_populates="product", cascade="all, delete-orphan")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    ebay_order_id = db.Column(db.String(120), nullable=False, index=True)
    buyer_name = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), nullable=False, server_default="detected")
    total_paid_by_buyer = db.Column(db.Numeric(10, 2), nullable=True)
    actual_supplier_cost = db.Column(db.Numeric(10, 2), nullable=True)
    error_log = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="orders")
    product = db.relationship("Product", back_populates="orders")
