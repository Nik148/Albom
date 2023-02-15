from app import create_app, cli
from app.search import add_to_index
from app.models import Post, User

app = create_app()
cli.register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')