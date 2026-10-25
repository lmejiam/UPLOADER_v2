import subprocess



def is_reachable(ip, timeout_seconds=5):

    # Send a single ping. Exit code 0 means the host answered.
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout  = subprocess.DEVNULL,
            stderr  = subprocess.DEVNULL,
            timeout = timeout_seconds,
        )
        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False

    except FileNotFoundError:
        print("Ping failed: the 'ping' command is not installed")
        return False
