\set ON_ERROR_STOP on
\pset pager off

SELECT current_database() = 'ai_workspace_test'
    AS database_is_safe
\gset

\if :database_is_safe
\echo 'Safe database confirmed: ai_workspace_test'
\else
\echo 'Refusing to run outside ai_workspace_test'
\quit
\endif

\echo 'Existing documents indexes'
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'documents'
ORDER BY indexname;

\echo 'Current get-by-id query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.documents
WHERE id = 1;

\echo 'Current ordered-list query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.documents
ORDER BY id;

BEGIN;

CREATE TABLE public.day22_documents_plan_lab (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    author_name text NOT NULL,
    is_published boolean NOT NULL DEFAULT false
);

INSERT INTO public.day22_documents_plan_lab (
    title,
    content,
    author_name,
    is_published
)
SELECT
    'Synthetic document ' || series_number,
    repeat('Synthetic content for plan analysis. ', 8),
    CASE
        WHEN series_number % 1000 = 0
            THEN 'Grace Hopper'
        ELSE 'Ada Lovelace'
    END,
    series_number % 2 = 0
FROM generate_series(1, 100000)
    AS generated(series_number);

ANALYZE public.day22_documents_plan_lab;

SELECT
    count(*) AS total_rows,
    count(*) FILTER (
        WHERE author_name = 'Grace Hopper'
    ) AS target_rows
FROM public.day22_documents_plan_lab;

\echo 'Lab primary-key lookup'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.day22_documents_plan_lab
WHERE id = 50000;

\echo 'Baseline run 1'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.day22_documents_plan_lab
WHERE author_name = 'Grace Hopper'
ORDER BY id;

\echo 'Baseline run 2'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.day22_documents_plan_lab
WHERE author_name = 'Grace Hopper'
ORDER BY id;

CREATE INDEX day22_plan_lab_author_name_idx
ON public.day22_documents_plan_lab (author_name);

ANALYZE public.day22_documents_plan_lab;

\echo 'Indexed run 1'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.day22_documents_plan_lab
WHERE author_name = 'Grace Hopper'
ORDER BY id;

\echo 'Indexed run 2'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, content, author_name, is_published
FROM public.day22_documents_plan_lab
WHERE author_name = 'Grace Hopper'
ORDER BY id;

ROLLBACK;

SELECT to_regclass(
    'public.day22_documents_plan_lab'
) AS lab_table_after_rollback;
