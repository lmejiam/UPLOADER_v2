import os
import time
import logging

log = logging.getLogger(__name__)



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
                log.info(f"Deleted {path}")
            except Exception as e:
                log.error(f"Delete failed {path}: {e}")

    return deleted