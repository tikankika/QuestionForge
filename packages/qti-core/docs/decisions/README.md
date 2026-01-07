# Architecture Decision Records (ADRs)

This directory contains records of architectural decisions made during the development of the QTI Generator for Inspera project.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

## Format

Each ADR follows this structure:
- **Title**: Short noun phrase
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: The issue motivating this decision
- **Decision**: The change being proposed or made
- **Consequences**: The results of applying this decision

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-markdown-input-format.md) | Use Markdown for Question Input Format | Accepted | 2025-10-30 |
| [002](002-xml-template-strategy.md) | QTI XML Template Strategy Based on Actual Exports | Accepted | 2025-10-30 |
| [003](003-pedagogical-framework-integration.md) | Integration of Three Pedagogical Frameworks | Accepted | 2025-10-30 |

## Creating a New ADR

When making a significant architectural decision:

1. Copy the template from an existing ADR
2. Number it sequentially (e.g., 004)
3. Fill in all sections
4. Update this README index
5. Commit with message: `docs(adr): add ADR-XXX [title]`

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
