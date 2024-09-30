import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()
# Замените следующие значения вашими учетными данными MySQL:
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
server = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_DATABASE")

# Пример строки подключения для MySQL
sqlalchemy_database_url = f"mysql+mysqlconnector://{username}:{password}@{server}:{port}/{db_name}"

engine = create_engine(
    sqlalchemy_database_url
)
sessionLocal = sessionmaker(bind=engine)
session = sessionLocal()

Base = declarative_base()