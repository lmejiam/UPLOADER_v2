import os 
import time



def delete_old_files(folder, max_age_days):

    if not os.path.isdir(folder):
        return []

    cutoff = time.time() - max_age_days * 24 * 60 * 60
    deleted = []

    for name in os.listdir(folder):

        path = os.path.join(folder,name)

        if not os.path.isfile(path):
            continue

        stat = os.stat(path)
        last_change = max(stat.st_mtime, stat.st_ctime)

        if last_change < cutoff:
            try:

                os.remove(path)
                deleted.append(path)
                print(f"Deleted {path}")
            except Exception as e:
                print(f"Delete failed {path}: {e}")

    return deleted