from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from data.category import Category
from data import db_session

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    is_private = BooleanField('Личное')
    categories = SelectMultipleField('Категории', coerce=int)
    submit = SubmitField('Применить')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db_sess = db_session.create_session()
        self.categories.choices = [(c.id, c.name) for c in db_sess.query(Category).all()]
