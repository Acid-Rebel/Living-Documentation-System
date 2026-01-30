from flask import Blueprint, Flask


app = Flask(__name__)


@app.route("/hello", methods=["GET", "POST"])
def hello_route():
    return "hello"


@app.route("/ping")
def ping_route():
    return "pong"


@app.get("/status")
def status_route():
    return {"status": "ok"}


blueprint = Blueprint("api", __name__)


@blueprint.route("/items", methods=["PUT"])
def blueprint_route():
    return "updated"


app.register_blueprint(blueprint, url_prefix="/api")
