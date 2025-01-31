from collections.abc import Iterable, Iterator

from faker import Faker
from pydantic import BaseModel

faker = Faker()


class User(BaseModel):
    name: str
    age: int


def generate_user() -> User:
    return User(
        name=faker.first_name(),
        age=faker.random_int(min=0, max=100),
    )


def generate_users(count: int) -> Iterator[User]:
    for _ in range(count):
        yield generate_user()


type OutputAsHtml = str


def render_users(users: Iterable[User]) -> OutputAsHtml:
    """Generate a list of strings with user names and ages.

    Use HTML tags for rendering.
    """
    users_array_of_str = [f"<li>{user.name}, {user.age} years old</li>" for user in users]

    users_str = "".join(users_array_of_str)

    return f"<ul>{users_str}</ul>"
