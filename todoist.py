import base64, binascii
from io import BytesIO
import json, requests, uuid

class MissingAuthToken(Exception):
    pass
class MissingProjectId(Exception):
    pass
class InvalidAttachment(Exception):
    pass
class TodoistError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)
    pass

def guess_file_type(data):
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg', 'jpg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png', 'png'
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return 'image/gif', 'gif'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'image/webp', 'webp'
    if data[4:8] == b'ftyp' and data[8:12] in (b'heic', b'heix', b'hevc', b'mif1'):
        return 'image/heic', 'heic'
    if data.startswith(b'%PDF-'):
        return 'application/pdf', 'pdf'
    return 'application/octet-stream', 'bin'

def decode_base64_file(base64_file):
    """Accepts either a bare base64 string or a full `data:<mime>;base64,...` URI."""
    mime_type = None

    if base64_file.startswith('data:'):
        header, separator, base64_file = base64_file.partition(',')
        if not separator:
            raise InvalidAttachment('Malformed data URI')
        mime_type = header[len('data:'):].split(';')[0] or None

    try:
        data = base64.b64decode(''.join(base64_file.split()), validate=True)
    except (binascii.Error, ValueError):
        raise InvalidAttachment('Attachment is not valid base64')

    if not data:
        raise InvalidAttachment('Attachment is empty')

    return data, mime_type

class todoist():
    def __init__(self, config):
        self.config = config
        self.todoist_endpoint = self.config.get('TODOIST_ENDPOINT')

        if not self.config.get('TODOIST_TOKEN'):
            raise MissingAuthToken()
        
        if not self.config.get('TODOIST_PROJECT_ID'):
            raise MissingProjectId()
        
    def get_headers(self, json_body=True):
        headers = {
            "Authorization": f"Bearer {self.config.get('TODOIST_TOKEN')}",
            "X-Request-Id": str(uuid.uuid4()),
        }

        # On multipart uploads requests sets Content-Type itself, boundary included.
        if json_body:
            headers["Content-Type"] = "application/json"

        return headers

    def parse_response(self, req):
        if not req.ok:
            raise TodoistError(req.status_code, req.text)

        try:
            return req.json()
        except ValueError:
            raise TodoistError(req.status_code, req.text)

    def send_post_request(self, path, body_data, files=None):
        if files:
            # multipart: the fields go as a plain form, not as a JSON blob
            payload = {"data": body_data, "files": files}
        else:
            payload = {"data": json.dumps(body_data)}

        req = requests.post(self.todoist_endpoint + path,
                               headers=self.get_headers(json_body=files is None),
                               **payload)

        return self.parse_response(req)
        
    def send_get_request(self, path):

        headers = self.get_headers()

        req = requests.get(self.todoist_endpoint + path,
                            headers=headers)

        return self.parse_response(req)

    def create_task(self, title, note = ""):
        task = {
            "content": title,
            "description": note,
            "project_id": self.config.get('TODOIST_PROJECT_ID')
        }
        return self.send_post_request("/tasks", task)

    def upload_attachment(self, base64_file, file_name=None):
        data, mime_type = decode_base64_file(base64_file)
        sniffed_type, extension = guess_file_type(data)

        if not file_name:
            file_name = f"attachment-{uuid.uuid4().hex[:8]}.{extension}"

        files = {
            "file": (file_name, BytesIO(data), mime_type or sniffed_type)
        }

        return self.send_post_request("/uploads", {}, files=files)

    def add_comment(self, task_id, attachment, content = ""):
        comment = {
            "task_id": task_id,
            # Todoist rejects an empty comment body even when a file rides along
            "content": content or attachment.get('file_name') or "Attachment",
            "attachment": attachment
        }
        return self.send_post_request("/comments", comment)
    
    def get_projects(self):
        return self.send_get_request("/projects")
