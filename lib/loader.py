import argparse
import shutil
import time
from itertools import cycle
from threading import Thread

from rich.progress import TextColumn


# Credit: https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running # noqa
class Loader:
    def __init__(self, desc="Processing", timeout=0.1):
        self.desc = desc
        self.timeout = timeout
        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            time.sleep(self.timeout)

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        self.done = True
        cols = shutil.get_terminal_size(fallback=(80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print("\r", end="", flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class LoadAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values if values is not None else True)


class ElapsedTimeColumn(TextColumn):
    def __init__(self, *args, **kwargs):
        super().__init__("{elapsed_time}", *args, **kwargs)
        self.start_time = time.time()

    def render(self, task):
        if task.completed == 100:
            return "[green]Completed[/green]"

        elapsed = time.time() - self.start_time
        formatted_time = f"[yellow]{elapsed:.2f}s[/yellow]"
        return formatted_time
