import os
import signal
import logging
import threading
from dotenv import load_dotenv

from files_finder   import find_files
from move_files     import move_files
from uploader       import get_s3_client, upload_files
from cleaner        import delete_old_files
from pinger         import is_reachable
from hmi_archiver   import archive_originals

load_dotenv()

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s %(levelname)-5s %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("uploader")

IMAGE_UPLOAD_FOLDER       = os.getenv("IMAGE_UPLOAD_FOLDER")
IMAGE_UPLOADED_FOLDER     = os.getenv("IMAGE_UPLOADED_FOLDER")
HMI_IMAGES_FOLDER         = os.getenv("HMI_IMAGES_FOLDER")
DATA_UPLOAD_FOLDER        = os.getenv("DATA_UPLOAD_FOLDER")
DATA_UPLOADED_FOLDER      = os.getenv("DATA_UPLOADED_FOLDER")
IMAGES_BUCKET             = os.getenv("IMAGES_BUCKET")
DATA_BUCKET               = os.getenv("DATA_BUCKET")


IMAGE_EXTENSIONS      = [".jpg", ".jpeg"]
DATA_EXTENSIONS       = [".txt", ".csv"]
SLEEP_SECONDS         = int(os.getenv("SLEEP_SECONDS","300"))
FILE_MIN_AGE_SECONDS  = int(os.getenv("FILE_MIN_AGE_SECONDS","30"))

CLEANUP_DAYS          = int(os.getenv("CLEANUP_DAYS","7"))
CLEANUP_ENABLED       = os.getenv("CLEANUP_ENABLED","true").lower() == "true"

PING_IP               = os.getenv("PING_IP")
PING_TIMEOUT_SECONDS  = int(os.getenv("PING_TIMEOUT_SECONDS","5"))



stop_event = threading.Event()


def handle_stop(signum, frame):
    log.info("Stop signal received, finishing current file before exiting...")
    stop_event.set()


if __name__ == "__main__":

    # docker stop sends SIGTERM, Ctrl+C sends SIGINT
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)

    log.info("Uploader starting")
    log.info(f"  Images: {IMAGE_UPLOAD_FOLDER} -> bucket '{IMAGES_BUCKET}', originals {HMI_IMAGES_FOLDER} -> {IMAGE_UPLOADED_FOLDER}")
    log.info(f"  Data:   {DATA_UPLOAD_FOLDER} -> bucket '{DATA_BUCKET}' -> {DATA_UPLOADED_FOLDER}")
    log.info(f"  S3 endpoint: {os.getenv('AWS_ENDPOINT_URL') or 'AWS default'}")
    log.info(f"  Scan every {SLEEP_SECONDS}s, skip files newer than {FILE_MIN_AGE_SECONDS}s")
    log.info(f"  Cleanup: {f'after {CLEANUP_DAYS} days' if CLEANUP_ENABLED else 'disabled'}")
    log.info(f"  Ping check: {PING_IP or 'disabled'}")

    s3 = get_s3_client()

    while not stop_event.is_set():

        # Only run the cycle if the host answers. If PING_IP is empty, always run.
        if PING_IP and not is_reachable(PING_IP, PING_TIMEOUT_SECONDS):
            log.warning(f"{PING_IP} not reachable, skipping this cycle")

        else:
            images  = find_files(IMAGE_UPLOAD_FOLDER, IMAGE_EXTENSIONS, FILE_MIN_AGE_SECONDS)
            data    = find_files(DATA_UPLOAD_FOLDER, DATA_EXTENSIONS, FILE_MIN_AGE_SECONDS)
            log.info(f"Scan: {len(images)} images, {len(data)} data files ready")

            if data:
                uploaded_data = upload_files(s3, data, DATA_BUCKET, stop_event)
                move_files(uploaded_data, DATA_UPLOADED_FOLDER)

            if images and not stop_event.is_set():
                uploaded_images = upload_files(s3, images, IMAGES_BUCKET, stop_event)
                archive_originals(uploaded_images, HMI_IMAGES_FOLDER, IMAGE_UPLOADED_FOLDER)

            if CLEANUP_ENABLED:
                delete_old_files(DATA_UPLOADED_FOLDER, CLEANUP_DAYS)
                delete_old_files(IMAGE_UPLOADED_FOLDER, CLEANUP_DAYS)

        # Like time.sleep, but wakes up right away on a stop signal
        stop_event.wait(SLEEP_SECONDS)

    log.info("Uploader stopped")
