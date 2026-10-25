import os
import signal
import threading
from dotenv import load_dotenv

from files_finder   import find_files
from move_files     import move_files
from uploader       import get_s3_client, upload_files
from cleaner        import delete_old_files
from pinger         import is_reachable

load_dotenv()

IMAGE_UPLOAD_FOLDER       = os.getenv("IMAGE_UPLOAD_FOLDER")
IMAGE_UPLOADED_FOLDER     = os.getenv("IMAGE_UPLOADED_FOLDER")
DATA_UPLOAD_FOLDER        = os.getenv("DATA_UPLOAD_FOLDER")
DATA_UPLOADED_FOLDER      = os.getenv("DATA_UPLOADED_FOLDER")
IMAGES_BUCKET             = os.getenv("IMAGES_BUCKET")
DATA_BUCKET               = os.getenv("DATA_BUCKET")


IMAGE_EXTENSIONS      = [".jpg", ".jpeg"]
DATA_EXTENSIONS       = [".txt", ".csv"]
SLEEP_SECONDS         = int(os.getenv("SLEEP_SECONDS","300"))
FILE_MIN_AGE_SECONDS  = int(os.getenv("FILE_MIN_AGE_SECONDS","30"))

CLEANUP_DAYS          = int(os.getenv("CLEANUP_DAYS","7"))

PING_IP               = os.getenv("PING_IP")
PING_TIMEOUT_SECONDS  = int(os.getenv("PING_TIMEOUT_SECONDS","5"))



stop_event = threading.Event()


def handle_stop(signum, frame):
    print("Stop signal received, finishing current file before exiting...")
    stop_event.set()


if __name__ == "__main__":

    # docker stop sends SIGTERM, Ctrl+C sends SIGINT
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)

    s3 = get_s3_client()

    while not stop_event.is_set():

        # Only run the cycle if the host answers. If PING_IP is empty, always run.
        if PING_IP and not is_reachable(PING_IP, PING_TIMEOUT_SECONDS):
            print(f"{PING_IP} not reachable, skipping this cycle")

        else:
            images  = find_files(IMAGE_UPLOAD_FOLDER, IMAGE_EXTENSIONS, FILE_MIN_AGE_SECONDS)
            data    = find_files(DATA_UPLOAD_FOLDER, DATA_EXTENSIONS, FILE_MIN_AGE_SECONDS)

            if data:
                uploaded_data = upload_files(s3, data, DATA_BUCKET, stop_event)
                move_files(uploaded_data, DATA_UPLOADED_FOLDER)

            if images and not stop_event.is_set():
                uploaded_images = upload_files(s3, images, IMAGES_BUCKET, stop_event)
                move_files(uploaded_images, IMAGE_UPLOADED_FOLDER)

            delete_old_files(DATA_UPLOADED_FOLDER, CLEANUP_DAYS)
            delete_old_files(IMAGE_UPLOADED_FOLDER, CLEANUP_DAYS)

        # Like time.sleep, but wakes up right away on a stop signal
        stop_event.wait(SLEEP_SECONDS)

    print("Uploader stopped")
