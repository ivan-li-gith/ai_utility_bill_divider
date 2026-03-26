from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from src.app.database.models import Base
from config import Config

load_dotenv()
connection_string = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}:3306/{Config.DB_NAME}"
engine = create_engine(connection_string, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# looks at all the models defined and creates the tables in db
def init_db():
    Base.metadata.create_all(bind=engine)