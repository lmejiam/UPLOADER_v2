import os
import errno
import logging

log = logging.getLogger(__name__)



def archive_originals(local_paths, originals_folder, archive_folder):

    # For each uploaded server copy: rename the original on the HMI into the archive
    # folder, then delete the server copy. The rename runs on the HMI itself, so no
    # image data goes back through the tunnel.
    os.makedirs(archive_folder, exist_ok = True)

    for local_path in local_paths:

        name     = os.path.basename(local_path)
        original = os.path.join(originals_folder, name)
        archived = os.path.join(archive_folder, name)

        try:
            if os.path.exists(original):
                # Overwrite an existing file with the same name in the archive
                if os.path.exists(archived):
                    os.remove(archived)
                    log.info(f"Overwriting existing {archived}")

                # os.rename, never shutil.move: a move that falls back to copying would
                # pull the whole image through the tunnel and push it back again
                os.rename(original, archived)
                log.info(f"Archived original {original} -> {archived}")

            elif os.path.exists(archived):
                # Already archived in an earlier cycle, only the server copy is left
                log.info(f"Original already archived {archived}")

            else:
                # Keep the server copy so nothing is lost. It will be retried next cycle.
                log.error(f"Original not found on HMI: {original}, keeping {local_path}")
                continue

            os.remove(local_path)
            log.info(f"Removed server copy {local_path}")

        except OSError as e:
            if e.errno == errno.EXDEV:
                log.error(f"Archive failed {name}: originals and archive folder must be on the same mount")
            else:
                log.error(f"Archive failed {name}: {e}")
