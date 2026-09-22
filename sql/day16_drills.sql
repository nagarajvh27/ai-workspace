WITH sample_documents (id, title, author_name, is_published) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', false),
        (2, 'Release checklist', 'Ada Lovelace', true),
        (3, 'API sketch', 'Grace Hopper', false),
        (4, 'SQL notes', 'Ada Lovelace', false)
)
SELECT id , title
from sample_documents
where author_name = 'Ada Lovelace'
AND is_published = false
order by id;


WITH candidate_authors (id, author_name) AS (
    VALUES
(1, 'Ada Lovelace'),
(2, NULL),
(3, 'Grace Hopper')
)
SELECT id
from candidate_authors
where author_name <> 'Ada Lovelace'
order by id;


WITH candidate_authors (id, author_name) AS (
    VALUES
(1, 'Ada Lovelace'),
(2, NULL),
(3, 'Grace Hopper')
)
SELECT id
from candidate_authors
where author_name <> 'Ada Lovelace'
or author_name  IS NULL
order by id;


WITH sample_documents (id, title, author_name, is_published) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', false),
        (2, 'Release checklist', 'Ada Lovelace', true),
        (3, 'API sketch', 'Grace Hopper', false),
        (4, 'SQL notes', 'Ada Lovelace', false)
)
SELECT
    d1.id AS first_id,
    d2.id AS second_id,
    d1.author_name
FROM sample_documents AS d1
JOIN sample_documents AS d2
    ON d1.author_name = d2.author_name
   AND d1.id < d2.id
ORDER BY d1.id, d2.id;


WITH sample_documents (id, title, author_name, is_published) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', false),
        (2, 'Release checklist', 'Ada Lovelace', true),
        (3, 'API sketch', 'Grace Hopper', false),
        (4, 'SQL notes', 'Ada Lovelace', false)
)
SELECT
    d1.id AS document_id,
    d2.id AS matching_document_id
FROM sample_documents AS d1
LEFT JOIN sample_documents AS d2
    ON d1.author_name = d2.author_name
   AND d1.id <> d2.id
WHERE d2.id IS NULL
ORDER BY d1.id, d2.id;
