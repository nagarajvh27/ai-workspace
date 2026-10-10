-- Day 23: CTE and window-function interview foundations.
-- All data is synthetic and exists only within each statement.

-- 1. Use chained CTEs to count published documents per author.
WITH documents (
    id,
    title,
    author_name,
    is_published,
    word_count
) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', true, 120),
        (2, 'Release checklist', 'Ada Lovelace', true, 90),
        (3, 'API sketch', 'Grace Hopper', false, 110),
        (4, 'SQL notes', 'Ada Lovelace', false, 90),
        (5, 'Testing notes', 'Grace Hopper', true, 70),
        (6, 'Index notes', 'Grace Hopper', true, 70),
        (7, 'Caching notes', 'Ada Lovelace', false, 60),
        (8, 'Network notes', 'Grace Hopper', false, 50)
),
published_documents AS (
    SELECT author_name
    FROM documents
    WHERE is_published = true
),
published_counts AS (
    SELECT
        author_name,
        count(*) AS document_count
    FROM published_documents
    GROUP BY author_name
)
SELECT author_name, document_count
FROM published_counts
ORDER BY document_count DESC, author_name;


-- 2. Preserve each document while adding its author's total.
WITH documents (
    id,
    title,
    author_name,
    is_published,
    word_count
) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', true, 120),
        (2, 'Release checklist', 'Ada Lovelace', true, 90),
        (3, 'API sketch', 'Grace Hopper', false, 110),
        (4, 'SQL notes', 'Ada Lovelace', false, 90),
        (5, 'Testing notes', 'Grace Hopper', true, 70),
        (6, 'Index notes', 'Grace Hopper', true, 70),
        (7, 'Caching notes', 'Ada Lovelace', false, 60),
        (8, 'Network notes', 'Grace Hopper', false, 50)
)
SELECT
    id,
    title,
    author_name,
    count(*) OVER (
        PARTITION BY author_name
    ) AS author_document_count
FROM documents
ORDER BY id;


-- 3. Compare ROW_NUMBER, RANK, and DENSE_RANK with ties.
WITH documents (
    id,
    title,
    author_name,
    is_published,
    word_count
) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', true, 120),
        (2, 'Release checklist', 'Ada Lovelace', true, 90),
        (3, 'API sketch', 'Grace Hopper', false, 110),
        (4, 'SQL notes', 'Ada Lovelace', false, 90),
        (5, 'Testing notes', 'Grace Hopper', true, 70),
        (6, 'Index notes', 'Grace Hopper', true, 70),
        (7, 'Caching notes', 'Ada Lovelace', false, 60),
        (8, 'Network notes', 'Grace Hopper', false, 50)
)
SELECT
    id,
    title,
    author_name,
    word_count,
    row_number() OVER (
        PARTITION BY author_name
        ORDER BY word_count DESC, id
    ) AS row_number,
    rank() OVER (
        PARTITION BY author_name
        ORDER BY word_count DESC
    ) AS rank,
    dense_rank() OVER (
        PARTITION BY author_name
        ORDER BY word_count DESC
    ) AS dense_rank
FROM documents
ORDER BY author_name, word_count DESC, id;


-- 4. Calculate a running word count for each author.
WITH documents (
    id,
    title,
    author_name,
    is_published,
    word_count
) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', true, 120),
        (2, 'Release checklist', 'Ada Lovelace', true, 90),
        (3, 'API sketch', 'Grace Hopper', false, 110),
        (4, 'SQL notes', 'Ada Lovelace', false, 90),
        (5, 'Testing notes', 'Grace Hopper', true, 70),
        (6, 'Index notes', 'Grace Hopper', true, 70),
        (7, 'Caching notes', 'Ada Lovelace', false, 60),
        (8, 'Network notes', 'Grace Hopper', false, 50)
)
SELECT
    id,
    title,
    author_name,
    word_count,
    sum(word_count) OVER (
        PARTITION BY author_name
        ORDER BY id
        ROWS BETWEEN UNBOUNDED PRECEDING
                 AND CURRENT ROW
    ) AS running_word_count
FROM documents
ORDER BY id;


-- 5. Compare each document with its author's previous document.
WITH documents (
    id,
    title,
    author_name,
    is_published,
    word_count
) AS (
    VALUES
        (1, 'Design notes', 'Ada Lovelace', true, 120),
        (2, 'Release checklist', 'Ada Lovelace', true, 90),
        (3, 'API sketch', 'Grace Hopper', false, 110),
        (4, 'SQL notes', 'Ada Lovelace', false, 90),
        (5, 'Testing notes', 'Grace Hopper', true, 70),
        (6, 'Index notes', 'Grace Hopper', true, 70),
        (7, 'Caching notes', 'Ada Lovelace', false, 60),
        (8, 'Network notes', 'Grace Hopper', false, 50)
),
document_comparisons AS (
    SELECT
        id,
        title,
        author_name,
        word_count,
        lag(word_count) OVER (
            PARTITION BY author_name
            ORDER BY id
        ) AS previous_word_count
    FROM documents
)
SELECT
    id,
    title,
    author_name,
    word_count,
    previous_word_count,
    word_count - previous_word_count AS word_count_change
FROM document_comparisons
ORDER BY id;
