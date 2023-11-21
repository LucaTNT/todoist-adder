from flask import Flask, redirect, jsonify, request, session
from config import Config
import json, os, sys, logging
import todoist

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'random-secret-key-not-that-important-in-this-use-case-i-think'

    if os.environ.get('DEBUG'):
        logging.setLevel(logging.DEBUG)

    try:
        app.todo = todoist.todoist(app.config)
    except todoist.MissingAuthToken:
        logging.error('Missing Todoist auth token')
        sys.exit(1)
    except todoist.MissingProjectId:
        logging.error('Missing Todoist project ID')
        sys.exit(1)

    return app

app = create_app()

class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code

@app.errorhandler(404)
def not_found(e):
    e = InvalidAPIUsage("Unavailable", 404)
    return jsonify(e.to_dict()), e.status_code


@app.route('/api/v1/todo', methods=["POST"])
def add_todo():
    if request.headers.get('Authorization') != app.config.get('AUTH_SECRET'):
        raise InvalidAPIUsage('Unauthorized', 401)
        
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage("Invalid JSON provided!")

    try:
        return app.todo.create_task(data.get('title'), data.get('note', ''))
    except todoist.TodoistError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
 
