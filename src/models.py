import uuid
from sqlalchemy import (
    Column, String, Text, DateTime, JSON, func, UniqueConstraint
)
from sqlalchemy.types import TypeDecorator, VARCHAR
import json
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# SQLite compatibility for UUID and ARRAY types
class UUID(TypeDecorator):
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return value
            
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return uuid.UUID(value)
            
    def __repr__(self):
        return "UUID()"

class ARRAY(TypeDecorator):
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return json.dumps(value)
            
    def process_result_value(self, value, dialect):
        if value is None:
            return []
        else:
            return json.loads(value)
            
    def __repr__(self):
        return "ARRAY()"

class RawOpportunity(Base):
    __tablename__ = "raw_opportunities"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source       = Column(String, nullable=False)
    external_id  = Column(String, nullable=False)
    raw_payload  = Column(JSON, nullable=False)
    ingested_at  = Column(DateTime, server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_source_external"),)

class Opportunity(Base):
    __tablename__ = "opportunities"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title       = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    what        = Column(String)
    when_at     = Column(DateTime)
    where_city  = Column(String)
    who         = Column(String)
    skills      = Column(ARRAY)
    topic_tags  = Column(ARRAY)
    source_url  = Column(String)
    created_at  = Column(DateTime, nullable=False)
    updated_at  = Column(DateTime, server_default=func.now(), nullable=False)
