from typing import TypedDict

from faker import Faker
from flask import Flask
from webargs import fields
from webargs.flaskparser import use_args

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


# if __name__ == "__main__":
#     app.run()
