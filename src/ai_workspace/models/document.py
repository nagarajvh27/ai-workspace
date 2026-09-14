from dataclasses import dataclass


def _normalize_title(title: str) -> str:
    if not isinstance(title, str):
        raise TypeError("Title must be a string")

    normalized_title = title.strip()

    if not normalized_title:
        raise ValueError("Title cannot be blank")

    return normalized_title



@dataclass
class Document:
    title: str
    content: str
    published: bool = False

    def _ensure_draft(self) -> None:
        if self.published:
            raise ValueError("Cannot modify a published document")



    def __post_init__(self) -> None:
        self.title = _normalize_title(self.title)


    def rename(self, new_title: str) -> None:
        self._ensure_draft()
        self.title = _normalize_title(new_title)


    def word_count(self) -> int:
        return len(self.content.split())


    def publish(self) -> None:

        if self.published:
            raise ValueError("Document is already published")

        self.published = True

    def update_content(self, new_content: str) -> None:
        self._ensure_draft()
        self.content = new_content

    def excerpt(self, max_chars: int) -> str:
        if not isinstance(max_chars, int) or isinstance(max_chars, bool):
            raise TypeError("max_chars must be an integer")

        if max_chars < 0:
            raise ValueError("max_chars cannot be negative")

        return self.content[:max_chars]
