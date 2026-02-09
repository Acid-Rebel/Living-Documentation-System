from flask import Flask

app = Flask(__name__)

@app.route("/api/v1/users", methods=["GET"])
def list_users():
    """List all users. This endpoint is deprecated."""
    pass

@app.route("/api/v1/profile", methods=["GET"])
def get_profile():
    """Get user profile."""
    pass
