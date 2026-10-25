import os
import shutil


def move_files(paths, target_folder):
    os.makedirs(target_folder, exist_ok = True)

    for path in paths:

        dest = os.path.join(target_folder, os.path.basename(path))

        try:
            shutil.move(path,dest)
            print(f"Moved {path} ----- {dest}")
        except Exception as e:
            print(f"Move failed {path}: {e}")
            