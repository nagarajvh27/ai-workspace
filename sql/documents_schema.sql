-- Day 16 design proposal; this is not an application migration.
CREATE TABLE documents (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    author_name text NOT NULL,
    is_published boolean NOT NULL DEFAULT false,
    CONSTRAINT documents_title_not_blank
        CHECK (btrim(title) <> ''),
    CONSTRAINT documents_author_name_not_blank
        CHECK (btrim(author_name) <> '')
);
