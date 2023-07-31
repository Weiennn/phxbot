from models import Base
from keyboards import engine

print('Creating tables...')
Base.metadata.create_all(engine)