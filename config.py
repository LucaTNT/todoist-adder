import os

class Config(object):
    TODOIST_ENDPOINT = "https://api.todoist.com/api/v1"
    TODOIST_TOKEN = os.environ.get('TODOIST_TOKEN')
    TODOIST_PROJECT_ID = os.environ.get('TODOIST_PROJECT_ID')

    AUTH_SECRET = os.environ.get('AUTH_SECRET') or 'supersecret'

