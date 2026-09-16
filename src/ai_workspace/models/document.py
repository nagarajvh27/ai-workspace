from dataclasses import dataclass, field

def _normalize_name(name: object) -> str:
    if not isinstance(name, str):
        raise TypeError("Author name must be text")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("Author name cannot be blank")

    return normalized_name

@dataclass(frozen=True)
class Author:
    name: str

    def __post_init__(self) -> None:
        normalized_name = _normalize_name(self.name)
        object.__setattr__(self, "name", normalized_name)


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
    author: Author
    _published: bool = field(default=False, init=False, repr=False)

    @property
    def is_published(self) -> bool:
        return self._published

    def _ensure_draft(self) -> None:
        if self._published:
            raise ValueError("Cannot modify a published document")



    def __post_init__(self) -> None:
        self.title = _normalize_title(self.title)

        if not isinstance(self.author, Author):
            raise TypeError("author must be an Author")


    def rename(self, new_title: str) -> None:
        self._ensure_draft()
        self.title = _normalize_title(new_title)


    def word_count(self) -> int:
        return len(self.content.split())


    def publish(self) -> None:

        if self._published:
            raise ValueError("Document is already published")

        self._published = True

    def update_content(self, new_content: str) -> None:
        self._ensure_draft()
        self.content = new_content

    def excerpt(self, max_chars: int) -> str:
        if not isinstance(max_chars, int) or isinstance(max_chars, bool):
            raise TypeError("max_chars must be an integer")

        if max_chars < 0:
            raise ValueError("max_chars cannot be negative")

        return self.content[:max_chars]
