# What is this
This tool exposes an HTTP endpoint that is used to easily add data to a Todoist project.
It was intended as an internal tool only, but I thought making it open source might be beneficial to someone.
I provide NO support, but you are free to use/edit it as you see fit.

# Basic info
Config is done through environment variables (see `config.py`)

POST to `/api/v1/todo` with the `Authorization header` set to whatever you have in `config.py` to send data to Todoist. You need to send a JSON payload like this:
`{"title": "The To Do Title", "note": "Your note"}`

GET `/api/v1/projects` (same `Authorization` header) to list your projects, which is handy for finding the `TODOIST_PROJECT_ID` to configure.

# Attachments
Add an `image` field to attach a file to the task. It takes either bare base64 or a full data URI:
`{"title": "The To Do Title", "note": "Your note", "image": "iVBORw0KGgo..."}`
`{"title": "The To Do Title", "image": "data:image/png;base64,iVBORw0KGgo..."}`

The file is uploaded to Todoist and then attached to the task as a comment, since that is the
only way Todoist exposes attachments. The MIME type comes from the data URI when you provide one,
otherwise it is guessed from the file's magic bytes (PNG, JPEG, GIF, WebP, HEIC and PDF are
recognised, anything else is sent as `application/octet-stream`).

The comment body cannot be empty, so it defaults to the file name. Pass `image_name` to set both
the file name and that comment text:
`{"title": "Receipt", "image": "...", "image_name": "receipt.jpg"}`

Note that the task is created before the attachment comment, so if the comment step fails you get
an error back with the task already saved. Bear that in mind if your client retries automatically.
