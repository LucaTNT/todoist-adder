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
        
    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.get('TODOIST_TOKEN')}",
            "X-Request-Id": str(uuid.uuid4()),
        }
        
    def send_post_request(self, path, body_data):
        body = json.dumps(body_data)
        headers = self.get_headers()

        req = requests.post(self.config.get('TODOIST_ENDPOINT') + path,
                               data=body,
                               headers=headers)

        try:
            return req.json()
        except:
            raise TodoistError(req.status_code, req.text)
        
    def send_get_request(self, path):

        headers = self.get_headers()

        req = requests.get(self.config.get('TODOIST_ENDPOINT') + path,
                            headers=headers)

        try:
            return req.json()
        except:
            raise TodoistError(req.status_code, req.text)

    def create_task(self, title, note = ""):
        task = {
            "content": title,
            "description": note,
            "project_id": self.config.get('TODOIST_PROJECT_ID')
        }
        return self.send_post_request("/tasks", task)
    
    def get_projects(self):
        return self.send_get_request("/projects")

