from core.database import Base, engine
from models.user import User

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
