import json, requests, uuid

class MissingAuthToken(Exception):
    pass
class MissingProjectId(Exception):
    pass
class TodoistError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)
    pass

class todoist():
    def __init__(self, config):
        self.config = config
        self.todoist_endpoint = "https://api.todoist.com/rest/v2"

        if not self.config.get('TODOIST_TOKEN'):
            raise MissingAuthToken()
        
        if not self.config.get('TODOIST_PROJECT_ID'):
            raise MissingProjectId()

    def create_task(self, title, note = ""):
        task = {
            "content": title,
            "description": note,
            "project_id": self.config.get('TODOIST_PROJECT_ID')
        }
        body = json.dumps(task)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.get('TODOIST_TOKEN')}",
            "X-Request-Id": str(uuid.uuid4()),
        }

        req = requests.post(self.config.get('TODOIST_ENDPOINT') + f"/tasks",
                               data=body,
                               headers=headers)

        try:
            return req.json()
        except:
            raise TodoistError(req.status_code, req.text)
