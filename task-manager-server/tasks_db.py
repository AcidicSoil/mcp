import uuid


class TaskDB:
    def __init__(self):
        self.tasks = {}

    def list_tasks(self):
        return list(self.tasks.values())

    def add_task(self, title, description=""):
        task_id = str(uuid.uuid4())
        task = {"id": task_id, "title": title, "description": description, "status": "pending"}
        self.tasks[task_id] = task
        return task

    def set_status(self, task_id, status):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            return True
        return False

    def get_task(self, task_id):
        return self.tasks.get(task_id, {})

    def next_task(self):
        for t in self.tasks.values():
            if t["status"] == "pending":
                return t
        return {}

    def update_task(self, task_id, title=None, description=None):
        if task_id in self.tasks:
            if title is not None:
                self.tasks[task_id]["title"] = title
            if description is not None:
                self.tasks[task_id]["description"] = description
            return self.tasks[task_id]
        return {}
