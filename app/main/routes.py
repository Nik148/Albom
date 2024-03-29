from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, abort, current_app, g, Response
from app.main import bp
from app import db, cache
from flask_login import current_user, login_required
from app.models import User, Post, likes
from datetime import datetime
from app.main.forms import EditProfileForm, AddPostForm, SearchForm
from flask_babel import get_locale, lazy_gettext as _l
from sqlalchemy.exc import IntegrityError
import os

@bp.before_request
def before_request():
    g.locale = get_locale()
    if current_app.elasticsearch:
        # Чтобы избежать csrf проверки, вводим в конструтор meta={'csrf': False}
        g.search_form = SearchForm(meta={'csrf': False})
    if current_user.is_authenticated:
        # print(current_user.last_seen)
        # user = cache.get(current_user.__repr__())
        # user.last_seen = current_user.last_seen = datetime.utcnow()
        # cache.set(user.__repr__(), user, timeout=600)
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # u = User.query.get(2)
        # print(u.last_seen)



@bp.route("/")
@bp.route("/main")
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template("main/main.html", posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('main/main.html',posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/profile/<username>/")
# @cache.cached(300) # Сохраняет в кэш с ключом view//profile/<username>/
def profile(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.profile', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.profile', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template("main/profile.html", user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/edit_profile", methods=("GET", "POST"))
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # Сохраняем файл по пути определенным в конфигурации+'avatars' и название фото изменяется на user.id
        if form.avatar.data:
            form.avatar.data.save(os.path.join(current_app.config['UPLOAD_PATH'], 'avatars/', str(current_user.id)))
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)

@bp.route("/add_post", methods=("GET", "POST"))
@login_required
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        post = Post(body=form.text.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        form.picture.data.save(os.path.join(current_app.config['UPLOAD_PATH'], post.get_picture()))
        # Удаление из кэша функции представления страницы пользователя
        cache.delete(f'view//profile/{current_user.username}/')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('main/add_post.html', form=form)

@bp.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user == None or current_user == user:
        return redirect(url_for("main.index"))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for("main.profile", username=username))

@bp.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user == None or current_user == user:
        return redirect(url_for("main.index"))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for("main.profile", username=username))

@bp.route("/profile/<username>/followers/")
# @cache.cached(120)
def followers(username):
    followers_list = User.query.filter_by(username=username).first().followers
    return render_template("main/people_list.html", people=followers_list)

@bp.route("/profile/<username>/followed/")
# @cache.cached(120)
def followed(username):
    followed_list = User.query.filter_by(username=username).first().followed
    return render_template("main/people_list.html", people=followed_list)

@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)

    if g.search_form.select.data == "People":
        people, total = User.search_prefix(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
        next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
        prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) if page > 1 else None
        return render_template('main/people_list.html', people=people, next_url=next_url, prev_url=prev_url)

    elif g.search_form.select.data == "Text":
        posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
        next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
        prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) if page > 1 else None
        return render_template('main/main.html', posts=posts, next_url=next_url, prev_url=prev_url)

@bp.route('/delete_post', methods=('POST',))
@login_required
def delete_post():
    username = request.json['username']
    post_id = request.json['post_id']
    if current_user.username != username:
        return Response(403)
    Post.delete_post(int(post_id))
    # cache.delete(f'view//profile/{current_user.username}/')
    return Response(status=200)

@bp.route('/like_increment', methods=("POST",))
@login_required
def like_increment():
    query = likes.insert().values(user_id=int(request.json['user_id']), post_id=int(request.json['post_id']))
    try:
        db.session.execute(query)
        db.session.commit()
    except IntegrityError:
        # Исключение срабытывающее на добавление строки, которая уже есть в бд
        # И на добавление несуществующих ключей
        return Response(status=400)
    return Response(status=200)

@bp.route('/like_decrement', methods=("POST",))
@login_required
def like_decrement():
    like = db.session.query(likes).filter(
        likes.c.user_id == int(request.json['user_id']),
        likes.c.post_id == int(request.json['post_id'])).delete()
    db.session.commit()
    return Response(status=200)
