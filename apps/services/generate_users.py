from collections.abc import Iterable, Iterator

from faker import Faker
from pydantic import BaseModel

faker = Faker()


class UserBase(BaseModel):
    name: str
    age: int


class UserWithId(UserBase):
    id: int


def generate_user() -> UserBase:
    return UserBase(
        name=faker.first_name(),
        age=faker.random_int(min=0, max=100),
    )


def generate_users(count: int) -> Iterator[UserBase]:
    for _ in range(count):
        yield generate_user()


type OutputAsHtml = str


def render_users(users: Iterable[UserBase]) -> OutputAsHtml:
    """Generate a list of strings with user names and ages.

    Use HTML tags for rendering.
    """
    users_array_of_str = [f"<li>{user.name}, {user.age} years old</li>" for user in users]

    users_str = "".join(users_array_of_str)

    return f"<ul>{users_str}</ul>"


class UsersResponse(BaseModel):
    users: list[UserBase]


def generate_users_for_json_response(amount: int) -> UsersResponse:
    return UsersResponse(users=generate_users(amount))
