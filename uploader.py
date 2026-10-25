import os
import boto3


def get_s3_client():
    return boto3.client("s3", endpoint_url = os.getenv("AWS_ENDPOINT_URL"))


def upload_files(s3, paths, bucket, stop_event=None):

    uploaded = []

    for path in paths:
        # Stop between files, never in the middle of one
        if stop_event and stop_event.is_set():
            break

        key = os.path.basename(path)

        try: 
            s3.upload_file(path, bucket, key)
            uploaded.append(path)

        except Exception as e:
            print(f"Failed {path}: {e}")

    return uploaded