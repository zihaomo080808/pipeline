import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# this line reads .env
from dotenv import load_dotenv
load_dotenv()

# add your src/ directory to path
import sys, pathlib
src_path = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models import Base  # your models

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Get database URL from environment variable
    url = os.getenv("DATABASE_URL")
    
    # Configure SQLAlchemy with URL from environment
    config_section = config.get_section(config.config_ini_section)
    config_section["sqlalchemy.url"] = url
    
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
