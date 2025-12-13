from abc import ABC, abstractmethod

class ModelClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Gera conteúdo a partir do prompt."""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Conta tokens no texto."""
        pass
