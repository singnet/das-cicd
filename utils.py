import re
import zipfile

def extract_zip(zip_path: str, extract_to: str):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def remove_special_chars(string: str):
    return re.sub(r"[^a-zA-Z]", "", string)
