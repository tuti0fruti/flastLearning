import datetime
from flask_login import UserMixin
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users' # чтобы обозначить, что User — не обычный класс, а именно класс модели, его необходимо унаследовать от объекта класса SqlAlchemyBase
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    email = sqlalchemy.Column(sqlalchemy.String,index=True, unique=True, nullable=True)
    
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,default=datetime.datetime.now)

    news = orm.relationship("News", back_populates='user')
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password) # устанавливает значение хеша пароля для переданной строки

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password) #  проверяет, правильный ли пароль ввел пользователь