import os
import sys
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from superlink import create_app


os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///syperlink_test_db"


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()



@pytest.mark.parametrize("url, status",
                            [("/", 302),
                             ("/a", 404),
                             ("/links/info", 200),
                             ("/links", 404),
                             ("/users/profile", 302),
                             ("/users/sign_in", 200),
                             ("/users/sign_up", 200),
                             ("/users/sign", 404),
                             ("/users/accept", 200),
                             ("/users/accept/w", 200)
                             ])
def test_get_request(client, url, status):
        response = client.get(url)
        assert response.status_code == status