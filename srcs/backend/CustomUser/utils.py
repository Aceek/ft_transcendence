import os


def avatar_image_path(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = f"{instance.username}_pp.{ext}"

    return os.path.join(f"avatars/{instance.id}", new_filename)
