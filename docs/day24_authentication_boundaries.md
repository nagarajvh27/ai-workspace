# Day 24: Authentication boundaries

## Purpose

Define which AI Workspace HTTP operations are intentionally public,
authenticated, or authorized before adding authentication code.

This is a design decision only. It does not change current route behavior.

## Terms

Authentication asks who the caller is.

Authorization asks what an authenticated caller may do.

Intentionally public means no caller identity is required by design.

## Current state

All existing routes currently accept anonymous requests.

The application has no user, account, principal, role, permission, tenant,
or document-owner model.

`author_name` is caller-supplied document data. It is not authenticated
identity and must not be used as proof of document ownership.

## Route policy

| Operation | Target boundary | Decision |
| --- | --- | --- |
| `GET /health` | Intentionally public | Keep public while it returns only basic availability information. |
| `GET /documents` | Authenticated and authorized | Collection visibility rules must be defined before enforcement. |
| `POST /documents` | Authenticated and authorized | The permission required to create a document must be defined. |
| `GET /documents/{document_id}` | Authenticated and authorized | Ownership, tenant, role, or sharing rules must be defined. |

The document-route classifications describe the intended security boundary.
They do not yet define a complete authorization policy.

## Application boundary

Credential extraction and validation belong at the FastAPI boundary.

A FastAPI dependency may later convert a credential into a small authenticated
principal. Missing or invalid required credentials should return `401
Unauthorized`. If bearer authentication is selected, that response should
include `WWW-Authenticate: Bearer`.

A caller whose identity is valid but whose permission is insufficient should
receive `403 Forbidden`.

Routes or application-level policy code should perform authorization before
the protected operation proceeds.

Services may receive identity information needed by a use case, such as an
actor ID, but should not parse raw credentials.

Domain models must not parse tokens, inspect HTTP headers, import FastAPI, or
depend on a particular identity provider.

Repository queries may eventually need authorization scope, such as an owner
or tenant ID. That schema and policy do not exist yet and must not be invented
implicitly.

## Open decisions

Before protecting document routes, decide:

- whether every authenticated caller may create documents;
- whether document lists contain all documents or only permitted documents;
- whether access is based on ownership, roles, tenants, explicit sharing, or
  another rule;
- whether `author_name` remains display metadata after authenticated identity
  is introduced;
- whether a denied document lookup returns `403` or hides existence with
  `404`.

## Lab decision

Do not add a fake authentication dependency to production routes yet.

A future isolated lab may use a clearly fake credential and principal to
demonstrate FastAPI dependency injection, `401`, and `403`. It must not be
presented as production security.

## Out of scope

- password storage;
- real JWT signing or verification;
- OAuth or OpenID Connect providers;
- sessions and refresh tokens;
- production identity infrastructure;
- production route, service, repository, or schema changes.
