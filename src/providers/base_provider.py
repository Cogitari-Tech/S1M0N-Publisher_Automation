from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import hashlib

@dataclass
class NewsItem:
    url: str
    title: str
    source_name: str
    published_date: datetime
    summary: Optional[str] = ""
    author: Optional[str] = None
    
    def get_hash(self) -> str:
        return hashlib.md5(self.url.encode('utf-8')).hexdigest()

class BaseNewsProvider(ABC):
    @abstractmethod
    def fetch(self, limit: int = 5) -> List[NewsItem]:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    
    def validate_config(self) -> bool:
        return True