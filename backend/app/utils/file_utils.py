import shutil
from fastapi import UploadFile

async def save_file(file: UploadFile, upload_dir: str):
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path
