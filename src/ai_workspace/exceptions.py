class DomainValidationError(ValueError):
    """Raised when input violates a domain rule."""


class PublishedDocumentError(DomainValidationError):
    """Raised when a caller tries to modify a published document."""
