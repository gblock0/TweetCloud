import contextlib
import itertools
import sys
import threading
import time
from typing import Final, Generator, Iterator, Optional, TextIO


@contextlib.contextmanager
def spinner(msg: Optional[str] = None, new_line: bool = True, done=True) -> Generator:
    spinner_cycle: Final[Iterator[str]] = itertools.chain(
        "-", itertools.cycle(["\b\\", "\b|", "\b/", "\b-"])
    )
    _stream: Final[TextIO] = sys.stdout
    stop_running: Final[threading.Event] = threading.Event()

    if msg:
        _stream.write(msg)
        _stream.write("...")
        _stream.flush()

    def init_spin():
        while not stop_running.is_set():
            _stream.write(next(spinner_cycle))
            _stream.flush()
            time.sleep(0.25)

        if done:
            _stream.write("\bdone")
            _stream.flush()

        else:
            _stream.write("\b \b")
            _stream.flush()

        if new_line:
            _stream.write("\n")
            _stream.flush()

    spin_thread = threading.Thread(target=init_spin)
    spin_thread.start()

    try:
        yield

    finally:
        if spin_thread:
            stop_running.set()
            spin_thread.join()
