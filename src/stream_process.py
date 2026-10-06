"""Small, dependency-free helpers for supervising GStreamer subprocesses."""

import subprocess


def stop_process(process):
    """Close a pipeline cleanly, escalating only when it will not exit."""
    if process.stdin is not None:
        try:
            process.stdin.close()
        except OSError:
            pass

    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def process_health(process):
    """Return serializable health without exposing subprocess implementation details."""
    if process is None:
        return {"running": False, "exit_code": None}

    exit_code = process.poll()
    return {"running": exit_code is None, "exit_code": exit_code}
