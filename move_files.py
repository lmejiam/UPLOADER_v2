import os
import shutil
import logging

log = logging.getLogger(__name__)


def move_files(paths, target_folder):
    os.makedirs(target_folder, exist_ok = True)

    for path in paths:

        dest = os.path.join(target_folder, os.path.basename(path))

        try:
            shutil.move(path,dest)
            log.info(f"Moved {path} -> {dest}")
        except Exception as e:
            log.error(f"Move failed {path}: {e}")
