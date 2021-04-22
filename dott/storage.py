from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def list_blobs(bucket_name, prefix):
    storage_client = storage.Client()
    return storage_client.list_blobs(bucket_name, prefix=prefix)

