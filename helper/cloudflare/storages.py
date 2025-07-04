from storages.backends.s3 import S3Storage


class StaticFileStorage(S3Storage):
    location = 'static'

class MediaFileStorage(S3Storage):
    location = 'uploads'

    