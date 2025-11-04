from rich.progress import Progress
from rich.progress import TaskID

class ProgressHandler:
    __process: Progress
    __tasks: dict[str, TaskID]
    __title: str

    def __init__(self):
        self.__process = Progress()
        self.__process.start()
        self.__tasks = {}
    
    def add_task(self, identifier: str, description: str) -> None:
        task_id = self.__process.add_task(description, visible=False)
        self.__tasks[identifier] = task_id
        
    def update_task(self, identifier: str, advance: float | None = None, total: float | None = None, visible: bool | None = None) -> None:
        if identifier in self.__tasks:
            task_id = self.__tasks[identifier]
            self.__process.update(task_id, advance=advance, total=total, visible=visible)
    
    def has_task(self, identifier: str) -> bool:
        return identifier in self.__tasks
    
    def print_title(self) -> None:
        print(self.__title)

    def stop(self) -> None:
        self.__process.stop()