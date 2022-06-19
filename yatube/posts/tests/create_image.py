from django.core.files.uploadedfile import SimpleUploadedFile

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


def create_image():
    image_name = f'small.gif'
    return SimpleUploadedFile(
        name=image_name,
        content=SMALL_GIF,
        content_type='image/gif'
    )
