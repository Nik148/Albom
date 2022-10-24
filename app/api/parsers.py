from app.api import rest_api

post_get_parser = rest_api.parser()
post_get_parser.add_argument(
    'page',
    type = int,
    location = 'args', # место поиска аргумента
    required = False # обязательный или необязательный аргумент(по умолчанию true)
)

post_post_parser = rest_api.parser()
post_post_parser.add_argument(
    'body',
    type = str,
    help = 'Body text is required',
    location = 'json'
)

post_put_parser = rest_api.parser()
post_put_parser.add_argument(
    'body',
    type = str,
    location = 'json'
)

auth_post_parser = rest_api.parser()
auth_post_parser.add_argument(
    'username',
    type = str,
    location = 'json'
)
auth_post_parser.add_argument(
    'password',
    type = str,
    location = 'json'
)