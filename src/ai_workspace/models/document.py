from dataclasses import dataclass


@dataclass
class Document:
    title: str
    content: str
    published: bool = False

    def word_count(self) -> int:
        return len(self.content.split())