# Отвечает за подключение к базе данных и создание сессии для работы с ней
import sqlalchemy as sa
import sqlalchemy.orm as orm # отвечает за функциональность ORM
from sqlalchemy.orm import Session # , отвечает за соединение с базой данных
import sqlalchemy.ext.declarative as dec # помогает объявить базу данных

SqlAlchemyBase = dec.declarative_base() # абстрактная декларативная база, в которой наследуются все модели
__factory = None #  фабрика подключений

def global_init(db_file): # Принимает на вход адрес базы данных
    # Проверяет, не создали ли мы уже фабрику подключений. 
    global __factory
    # Если уже создали, то завершаем работу, так как начальную инициализацию надо проводить только единожды
    if __factory:
        return
    
    # Проверяем, что нам указали непустой адрес базы данны
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    
    # создаем строку подключения conn_str (она состоит из типа базы данных, адреса до базы данных и параметров подключения), которую передаем Sqlalchemy для того, чтобы она выбрала правильный движок работы с базой данных (переменная engine). В нашем случае это будет движок для работы с SQLite базами данных
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = sa.create_engine(conn_str, echo=False)
    # Создаем фабрику подключений к нашей базе данных, которая будет работать с нужным нам движком
    __factory = orm.sessionmaker(bind=engine)
    
    # Импортируем все из файла __all_models.py — именно тут SQLalchemy узнает о всех наших моделях
    from . import __all_models
    
    #  Заставляем нашу базу данных создать все объекты, которые она пока не создала
    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session: # нужна для получения сессии подключения к нашей базе данных
    global __factory
    return __factory()