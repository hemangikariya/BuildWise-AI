from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# Create engine for PostgreSQL
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# SessionLocal is the DB session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables() -> None:
    """Import models to register them with Base, and create tables."""
    from app.models.user import User, Role
    from app.models.project import Project, ProjectVersion, AIChat
    from app.models.agent import AgentRun
    from app.models.rag import KnowledgeBase, Report
    from app.models.logs import AuditLog, SystemLog
    
    Base.metadata.create_all(bind=engine)
    
    # Seed roles
    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN")
            db.add(admin_role)
        
        user_role = db.query(Role).filter(Role.name == "USER").first()
        if not user_role:
            user_role = Role(name="USER")
            db.add(user_role)
            
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

