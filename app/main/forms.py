from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import lazy_gettext as _l
from flask import request, current_app
from werkzeug.utils import secure_filename
import os.path

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    avatar = FileField('Avatar')
    submit = SubmitField('Submit')

    def validate_avatar(self, avatar):
            # Безопасно извлекаем имя файла
            filename = secure_filename(avatar.data.filename)
            file_ext = os.path.splitext(filename)[1]
            # file_ext = os.path.splitext(filename)[1] #filename.rsplit('.', 1)[1].lower()
            # Если неразрешенный формат файла и файла существует, то вызывается исключение
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] and filename:
                raise ValidationError('Please use a different format of photo.')

class AddPostForm(FlaskForm):
    text = TextAreaField('Text', validators=[Length(min=0, max=200)])
    picture = FileField('Picture')
    submit = SubmitField('Submit')    

    def validate_picture(self, picture):
            # Безопасно извлекаем имя файла
            filename = secure_filename(picture.data.filename)
            file_ext = os.path.splitext(filename)[1]
            # file_ext = os.path.splitext(filename)[1] #filename.rsplit('.', 1)[1].lower()
            # Если неразрешенный формат файла и файла существует, то вызывается исключение
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] and filename:
                raise ValidationError('Please use a different format of photo.')    

class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])
    select = RadioField('Select', choices=('People', 'Text'), default='People', validators=[DataRequired()])

# Для этой формы я решил не использовать кнопку отправки. 
# Для формы, которая имеет текстовое поле, браузер отправит форму, 
# когда вы нажмете Enter с фокусом на поле, поэтому кнопка не нужна.
# Я также добавил функцию конструктора __init__, 
# которая предоставляет значения для аргументов formdata и csrf_enabled, если они не предоставляются вызывающим.
# Аргумент formdata определяет, откуда Flask-WTF получает формы. 
# По умолчанию используется request.form, где Flask помещает значения форм, которые передаются через запрос POST. 
# Формы, представленные через запрос GET, получают значения полей в строке запроса, 
# поэтому мне нужно указать Flask-WTF на request.args, где Flask записывает аргументы строки запроса. 
# И, как вы помните, формы добавили CSRF-защиту по умолчанию, с добавлением токена CSRF, 
# который добавляется в форму через конструкцию form.hidden_tag() в шаблонах. 
# Для работы с интерактивными поисковыми ссылками CSRF-защиту необходимо отключить, 
# поэтому я устанавливаю csrf_enabled в False, так что Flask-WTF знает, 
# что ему необходимо обходить проверку CSRF для этой формы.
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf' not in kwargs:
            kwargs['csrf'] = False
        super(SearchForm, self).__init__(*args, **kwargs)