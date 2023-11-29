import socket

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export

# noqa (would need to use a docker container to test this)
@export
def find_open_port(start_port: int, max_tries: int = 100, step: int = 10) -> int:
    for i in range(max_tries):
        port = start_port + i * step
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("localhost", port))
            if result != 0:
                return port
    raise Exception("Could not find an open port")
