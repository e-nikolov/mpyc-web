from .channels import chanSync


def fetch(filename: str):
    return chanSync.fetch(filename).to_py()
