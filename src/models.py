from sqlalchemy import (
    Column, String, Text, DateTime, JSON, ARRAY, func, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RawOpportunity(Base):
    __tablename__ = "raw_opportunities"
    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    source       = Column(String, nullable=False)
    external_id  = Column(String, nullable=False)
    raw_payload  = Column(JSON, nullable=False)
    ingested_at  = Column(DateTime, server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_source_external"),)

class Opportunity(Base):
    __tablename__ = "opportunities"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    title       = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    what        = Column(String)
    when_at     = Column(DateTime)
    where_city  = Column(String)
    who         = Column(String)
    skills      = Column(ARRAY(String))
    topic_tags  = Column(ARRAY(String))
    source_url  = Column(String)
    created_at  = Column(DateTime, nullable=False)
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
