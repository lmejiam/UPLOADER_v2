import os
import logging
import boto3

log = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client("s3", endpoint_url = os.getenv("AWS_ENDPOINT_URL"))


def upload_files(s3, paths, bucket, stop_event=None):

    uploaded = []
    total = len(paths)
    log.info(f"Uploading {total} files to bucket '{bucket}'")

    for i, path in enumerate(paths, start=1):
        # Stop between files, never in the middle of one
        if stop_event and stop_event.is_set():
            log.info(f"Stop requested, {total - i + 1} files left for next run")
            break

        key = os.path.basename(path)

        try:
            s3.upload_file(path, bucket, key)
            uploaded.append(path)
            log.info(f"Uploaded {key} ({i}/{total})")

        except Exception as e:
            log.error(f"Upload failed {key} ({i}/{total}): {e}")

    return uploaded
