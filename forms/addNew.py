from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data.category import Category
from data.db_session import create_session

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    is_private = BooleanField('Личное')
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        db_sess = create_session()
        self.category.choices = [(category.id, category.name) for category in db_sess.query(Category).order_by(Category.name).all()]
