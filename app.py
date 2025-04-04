import random
import time
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import TypedDict

import magic
from faker import Faker
from flask import Flask, Response, render_template, request, send_file
from pydantic import BaseModel, Field
from webargs import fields
from webargs.flaskparser import use_args

from apps.db_utils.create_db_table import create_db_table
from apps.db_utils.db_connection import DBConnection
from apps.services.generate_users import (
    UserBase,
    UserWithId,
    generate_users,
    generate_users_for_json_response,
    render_users,
)
from apps.settings import FILES_PATH

app = Flask(__name__)

create_db_table()


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


@app.route("/example-sql/users", methods=["POST"])
def example_sql_create_user() -> dict:
    data_raw = request.json
    user_validated = UserBase.model_validate(data_raw)

    # Make SQL query to insert user into the database.
    # Then get actual user from the database.
    # Validate it.
    # Return it for serialization.
    with DBConnection() as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, age) VALUES (:name, :age) RETURNING id;",
            user_validated.model_dump(mode="json"),
        )
        user_id = cursor.fetchone()[0]

        # Get the user from the database
        cursor.execute(
            "SELECT id, name, age FROM users WHERE id = :id;",
            {"id": user_id},
        )

        user_data_as_db_row = cursor.fetchone()
        user_data_as_dict = dict(user_data_as_db_row)
        user_saved = UserWithId.model_validate(user_data_as_dict)

    return user_saved.model_dump(mode="json")


# Implement files download. Generate random text as a file. Return it as a file.


def generate_random_text() -> str:
    faker = Faker()
    return faker.text(max_nb_chars=1000)


@app.route("/example-files/download")
def example_files_download() -> Response:
    file_name = "random_text.txt"
    content = generate_random_text()

    return Response(
        content,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            # "Content-Disposition": f'filename="{file_name}"',
            #
            # "Content-Disposition": f'attachment; filename="../../../{file_name}"',
            # Attacks: RFI, LFI, Path Traversal
        },
        mimetype="text/plain",
    )


@app.route("/example-files/download-2")
def example_files_download_2() -> Response:
    file_name = "random_text_2.txt"
    content = generate_random_text()

    # Convert string to bytes
    content_as_bytes = content.encode()

    files_as_bytes_io = BytesIO()
    files_as_bytes_io.write(content_as_bytes)
    files_as_bytes_io.seek(0)
    mimetype = magic.from_buffer(files_as_bytes_io.read(2048), mime=True)
    files_as_bytes_io.seek(0)

    return send_file(
        path_or_file=files_as_bytes_io,
        as_attachment=True,
        download_name=file_name,
        # mimetype="text/plain",
        mimetype=mimetype,
    )


@app.route("/example-files/download-3")
def example_files_download_3() -> Response:
    file_name = "random_text_3.txt"
    content = generate_random_text()

    with NamedTemporaryFile(mode="wb", suffix=".txt") as temp_file:
        logger = app.logger
        logger.info(f"Temporary file name: {temp_file.name}")

        temp_file.write(content.encode())
        temp_file.seek(0)

        return send_file(
            path_or_file=temp_file.name,
            as_attachment=True,
            download_name=file_name,
            # mimetype="text/plain",
            mimetype="text/plain",
        )


@app.route("/example-files/download-4")
def example_files_download_4() -> Response:
    path_to_image = FILES_PATH.joinpath("img.png")

    mimetype = magic.from_file(path_to_image, mime=True)

    return send_file(
        path_or_file=path_to_image,
        # as_attachment=True,
        download_name=path_to_image.name,
        # mimetype="image/png",
        mimetype=mimetype,
        # mimetype="plain/text",
    )


# TODO: Upload file to the server.
# Save it to the server. Return information about the file.
class UploadedFileInfo(BaseModel):
    file_name: str
    file_storage_id: str = Field(
        description="For example, 'path to file', if it is a file on the server.",
    )
    file_size: int
    mime_type: str


@app.route("/example-files/upload", methods=["POST"])
def example_files_upload() -> dict:
    # Get file from POST request. Save it to the server. Return the file name.

    file = request.files["file"]
    file_name = file.filename
    # TODO: Add file name validation.
    path_to_file = FILES_PATH / file_name
    file.save(path_to_file)

    file_size = path_to_file.stat().st_size

    mime_type = magic.Magic(mime=True).from_file(str(path_to_file))
    # mime_type = file.mimetype

    file_info = UploadedFileInfo(
        file_name=file_name,
        file_storage_id=str(path_to_file),
        file_size=file_size,
        mime_type=mime_type,
    )

    return file_info.model_dump(mode="json")


# if __name__ == "__main__":
#     app.run()
