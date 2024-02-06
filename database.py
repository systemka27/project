from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


db_connection_string = "postgresql+psycopg2://postgres:1234@127.0.0.1:5432/database"



#Создает объект engine, который предоставляет интерфейс для взаимодействия с базой данных.
# В данном случае, используется созданная строка подключения.
engine = create_engine(db_connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #что делает SessionLocal??
Base = declarative_base()

#Создает все таблицы, определенные в моделях данных, связанных с объектом engine.
# SQLAlchemy автоматически создаст базу данных и таблицы на основе определенных классов.
Base.metadata.create_all(bind=engine)

print("База данных и таблица созданы")

#autoflush=False - автоматическая синхронизация с базой данных не будет выполняться при каждом
# изменении объектов в сеансе, что полезно в некоторых сценариях производительности.
# bind=engine указывает, что сеанс будет связан с указанным движком (engine).