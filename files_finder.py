import os
import time



def find_files(folder, extensions, min_age_seconds=0):

    exts = tuple(e.lower() for e in extensions)
    files = []
    now = time.time()

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and name.lower().endswith(exts):

            # Skip files changed recently, they may still be copying in.
            # ctime is checked too because copy tools can reset mtime to an old date.
            stat = os.stat(path)
            last_change = max(stat.st_mtime, stat.st_ctime)
            if now - last_change < min_age_seconds:
                continue

            files.append(path)
    return files
