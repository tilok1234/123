import queue

class CommandBus:
    def __init__(self):
        self._q = queue.Queue()

    def push(self, cmd: tuple) -> None:
        self._q.put(cmd)

    def get_nowait(self) -> tuple:
        return self._q.get_nowait()

    def empty(self) -> bool:
        return self._q.empty()
