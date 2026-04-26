from sqlalchemy import Column, LargeBinary, BigInteger, SmallInteger, Text, DateTime, Boolean, JSON, Numeric
from sqlalchemy.sql import func
from .db import Base

class Seed(Base):
    __tablename__ = "seeds"
    seed_id = Column(LargeBinary, primary_key=True)
    token_id = Column(BigInteger)
    parent_seed_id = Column(LargeBinary)
    state = Column(SmallInteger)
    manifest_hash = Column(LargeBinary)
    ciphertext_hash = Column(LargeBinary)
    public_summary_hash = Column(LargeBinary)
    payload_uri = Column(Text)
    sovereign_package_hash = Column(LargeBinary)
    sovereign_package_uri = Column(Text)
    sovereign_contract = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
