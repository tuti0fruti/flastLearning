import datetime
from flask import Flask, abort, make_response, redirect, render_template, request, session, url_for
from data import db_session
from data.category import Category
from data.users import User
from data.news import News
from forms.addNew import NewsForm
from forms.category import CategoryForm
from forms.user import LoginForm, RegisterForm
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/blogs.sqlite") # добавляем вызов глобальной инициализации всего, что связано с БД

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route("/")
def index():
    db_sess = db_session.create_session()
    
    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/cookie_test")
def cookie_test():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(render_template("index.html", news=news))
        res.set_cookie("visits_count", '1', max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response("Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',max_age=60 * 60 * 24 * 365 * 2)
    
    return res

@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',form=form,message="Пароли не совпадают")
        db_sess = db_session.create_session()
       
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")
        
        user = User(
        name=form.name.data,
        email=form.email.data,
        about=form.about.data
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        
        return redirect('/login')
    
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # Проверяем, существует ли пользователь и пароль верен
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # Успешная аутентификация
            return redirect('/') # Перенаправление на страницу после входа
        else:
            # Неправильный логин или пароль
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html', form=form)

@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News(
            title=form.title.data,
            content=form.content.data,
            is_private=form.is_private.data,
            user_id=current_user.id,
            categories=[db_sess.query(Category).get(id) for id in form.categories.data]
        )
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', form=form)

@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user_id == current_user.id).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            form.categories.data = [category.id for category in news.categories]
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user_id == current_user.id).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            news.categories = [db_sess.query(Category).get(id) for id in form.categories.data]
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)

@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user_id == current_user.id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        category = Category(name=form.name.data)
        db_sess.add(category)
        db_sess.commit()
        return redirect('/')
    return render_template('category.html', title='Добавление категории', form=form)

def main():
    db_sess = db_session.create_session()

    user = User()
    # user.name = "Пользователь 1"
    # user.about = "биография пользователя 1"
    # user.email = "email@email1.ru"
    # db_sess.add(user)
    # db_sess.commit()

    # user = User()
    # user.name = "Пользователь 2"
    # user.about = "биография пользователя 2"
    # user.email = "email@email2.ru"
    # db_sess.add(user)
    # db_sess.commit()

    # user = User()
    # user.name = "Пользователь 3"
    # user.about = "биография пользователя 3"
    # user.email = "email@email3ru"
    # db_sess.add(user)
    # db_sess.commit()

    # выбор первого пользователя
    user = db_sess.query(User).first()
    print(user.name)

    # вывод всех пользователей
    for user in db_sess.query(User).all():
        print(user)

    # вывод пользователей по условию используя AND
    for user in db_sess.query(User).filter(User.id > 1, User.email.notilike("%1%")):
        print(user.name)

    # вывод пользователей по условию используя OR
    for user in db_sess.query(User).filter((User.id > 1) | (User.email.notilike("%1%"))):
        print(user.name)

    # Изменение пользователя
    # user = db_sess.query(User).filter(User.id == 1).first()
    # print(user.name)
    # user.name = "Измененное имя пользователя"
    # user.created_date = datetime.datetime.now()
    # db_sess.commit()

    # Удаление пользователей по фильтру
    # db_sess.query(User).filter(User.id >= 3).delete()
    # db_sess.commit()

    # Удаление пользователя по ID
    # user = db_sess.query(User).filter(User.id == 2).first()
    # db_sess.delete(user)
    # db_sess.commit()

    # Добавление новости для пользователя с id 1
    # news = News(title="Первая новость", content="Привет блог!",
    # user_id=1, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()

    # Добавление новости через объект класса
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Вторая новость", content="Уже вторая запись!",
    # user=user, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()
    
    # Добавление новости через список
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Личная запись", content="Эта запись личная",
    # is_private=True)
    # user.news.append(news)
    # db_sess.commit()

    # Просмотр новостей пользователя
    for news in user.news:
        print(news)

if __name__ == '__main__':
    app.run(port=700, host='127.0.0.1')
    #main()