from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4


class BaseStorageService(ABC):
    @abstractmethod
    def upload(self, file_bytes: bytes, filename: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete(self, file_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        raise NotImplementedError


class LocalStorageService(BaseStorageService):
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file_bytes: bytes, filename: str) -> str:
        safe_name = f"{uuid4().hex}_{filename.replace(' ', '_')}"
        target_path = self.upload_dir / safe_name
        target_path.write_bytes(file_bytes)
        return str(target_path)

    def delete(self, file_path: str) -> None:
        path = Path(file_path)
        if path.exists():
            path.unlink()

    def get_url(self, file_path: str) -> str:
        return file_path
