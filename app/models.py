from email.policy import default
from app import db, login, cache
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from flask import current_app, g
import os
from time import time
import jwt
from app.search import add_to_index, remove_from_index, query_index, query_prefix_index
import uuid

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

users_roles = db.Table('users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

likes = db.Table('likes',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.UniqueConstraint('post_id', 'user_id')
)

chat_followers = db.Table('chat_followers',
    db.Column('chat_id', UUID(as_uuid=True), db.ForeignKey('chat.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class SearchableMixin(object):
    # Для Elasticsearch
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def search_prefix(cls, expression, page, per_page):
        ids, total = query_prefix_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class User(UserMixin, db.Model, SearchableMixin):
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140), default='')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    role = db.relationship('Role', secondary=users_roles, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    # Декоратор @cache.memoize использует функцию repr() для просмотра переданных аргументов,
    # так что, если у объекта есть метод __repr__, который возвращает уникально идентифицирующую строку для этого объекта, 
    # то она будет использоваться как часть ключа кэша.
    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)
        
    # def check_avatar(self) -> bool:
    #     return os.path.exists("app/static/images/"+self.avatar())

    def get_avatar(self):
        # Проверка существования аватарки
        if os.path.exists("app/static/images/avatars/"+str(self.id)):
            return 'avatars/'+str(self.id)
        else:
            return 'avatars/not-found.jpg'
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    @cache.memoize(300) # Не может серилизовать классы запросов sqlalchemy
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
        
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def get_new_user_token(username, email, password, expires_in=600):
        return jwt.encode({'username': username, 'email': email, 'password': password, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_new_user_token(token):
        try:
            token_decode = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])
        except:
            return
        return token_decode 


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    # Реализация с кэшами, имеет проблемы при вызовах внешних ключей с ленивой загрузкой
    # user = f'<User {id}>'
    # user_obj = pickle.loads(cache.get(user)) if cache.get(user) else None
    # if user_obj is None:
    #     print('Caching...')
    #     query = User.query.options(joinedload('followed'), joinedload('role')).get(1)
    #     user_obj = pickle.dumps(User.query.get(int(id)))
    #     cache.set(user, user_obj, timeout=300)
    #     return query
    # return user_obj

    # Стандарт
  return User.query.get(int(id))

class Role(db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "<Model Role `{}`>".format(self.name)

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('User', secondary=likes, backref=db.backref('liked_posts', lazy='dynamic')  ,lazy='dynamic')

    def get_picture(self):
        return 'pictures/'+str(self.id)

    def is_liked(self, user):
        print(self.likes.filter(likes.c.user_id == user.id).count() > 0)
        return (self.likes.filter(
            likes.c.user_id == user.id).count() > 0)

    @staticmethod
    def delete_post(id):
        post = Post.query.filter_by(id=id).first()
        if post:
            # Проверка существования картинки
            if os.path.exists("app/static/images/pictures/"+str(id)):            
                os.remove(current_app.config["UPLOAD_PATH"] + post.get_picture())
            db.session.delete(post)
            db.session.commit()


    def __repr__(self):
        return '<Post {}>'.format(self.id)

class AnonymousUser(AnonymousUserMixin):
    def is_following(self, user):
        return False
    

class Chat(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String())


class Message(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chat.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String())
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)