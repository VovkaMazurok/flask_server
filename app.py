from flask import Flask

# shared__flask_example__2024_12_10
app = Flask(__name__)


@app.route("/")
def hello_world():  # put application's code here
    return "Hello World!"


if __name__ == "__main__":
    app.run()
