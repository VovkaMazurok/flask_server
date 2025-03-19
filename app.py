import random
import time
from typing import TypedDict

from faker import Faker
from flask import Flask, render_template, request
from webargs import fields
from webargs.flaskparser import use_args

from apps.services.generate_users import (
    UserBase,
    UserWithId,
    generate_users,
    generate_users_for_json_response,
    render_users,
)

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    faker = Faker()
    return f"Hello {faker.name()}!"


def hello_world_other() -> str:
    return "Hello World! Other."


# Registering routes as function, not as decorator.
app.route("/other")(hello_world_other)
app.route("/other/2")(hello_world_other)


@app.route("/health")
def health() -> str:
    return "OK"


def generate_greeting(name: str, age: int) -> str:
    return f"Hello {name}! You are {age} years old."


# http://127.0.0.1:5000/example-simple/hi/Alex/70
@app.route("/example-simple/hi/<name>/<int:age>")
@app.route("/example-simple/hi/<name>")
@app.route("/example-simple/hi")
def example_simple_hi(
    name: str = "Bob",
    age: int = 42,
) -> str:
    return generate_greeting(name=name, age=age)


class ExampleSimpleArgsAsDict(
    TypedDict,
    # total=False,
):
    name: str
    age: int


@app.route("/example-simple/hello")
@use_args(
    {"name": fields.Str(missing="Bob"), "age": fields.Int(missing=42)},
    location="query",
)
def example_simple_hello(
    # args: dict,
    args: ExampleSimpleArgsAsDict,
) -> str:
    name = args["name"]
    age = args["age"]

    return generate_greeting(name=name, age=age)


@app.route("/template")
def render_by_template_view() -> str:
    return render_template("index.html")


@app.route("/example-text/fake/users")
# @use_args(
#     {"is_wait": fields.Bool(missing=False), "generator_id": fields.Int(missing=0)},
#     location="query",
# )
def example_text_fake_users() -> str:
    users = generate_users(count=2)

    return render_users(users=users)


@app.route("/example-json/users")
@use_args(
    {
        "amount": fields.Int(missing=2),
        "is_wait": fields.Bool(missing=False),
        "generator_id": fields.Int(missing=0),
    },
    location="query",
)
def example_json_get_users(args: dict) -> list:
    amount: int = args["amount"]
    is_wait: bool = args["is_wait"]
    generator_id: int = args["generator_id"]

    if is_wait:
        time_to_wait = random.randint(1, 5)  # noqa: S311
        logger = app.logger
        logger.info(f"Time to wait: {time_to_wait}", extra={"generator_id": generator_id})
        # Simulate waiting
        time.sleep(time_to_wait)
        logger.info("Wait done", extra={"generator_id": generator_id})

    users_for_json = generate_users_for_json_response(amount=amount)

    return users_for_json.model_dump(mode="json")


@app.route("/example-json/users", methods=["POST"])
def example_json_create_user() -> dict:
    data_raw = request.json
    user = UserBase.model_validate(data_raw)

    # Simulate saving to a database
    user_id = 1

    user_created = UserWithId(
        id=user_id,
        **user.model_dump(mode="python"),
    )

    return user_created.model_dump(mode="json")


# Create curl command to test the endpoint
# curl -X POST -H "Content-Type: application/json" -d '{"name": "John", "age": 30}' http://site.homework.local.net:60000/example-json/users


# if __name__ == "__main__":
#     app.run()
