# Commit-As-Prompt Examples

## Example 1: OAuth2 Support (Prompt Context)

```bash
git commit -m "prompt(auth): add OAuth2 login support" -m "WHAT: refactor auth middleware to support OAuth2.
WHY: required for new security policy #2345.
HOW: introduced authorization code flow to replace BasicAuth; maintains legacy token compatibility."
```

## Example 2: Cleanup (Prompt Context)

```bash
git commit -m "prompt(api): remove deprecated endpoints" -m "WHAT: prune legacy v1 API endpoints.
WHY: reduce maintenance surface for v2 release.
HOW: dropped v1 handlers and updated docs; bumped version identifier."
```

## Example 3: Standard Feature

```bash
git commit -m "feat(ui): add dark mode toggle" -m "WHAT: settings page UI for theme switching.
WHY: user feedback for low-light accessibility #1234.
HOW: used CSS variables and localStorage for persistence."
```

## AI Context Aggregation (Reference)

When multiple `prompt:` commits are aggregated, they form a clear timeline for AI tools:

```text
<Context>
1. [WHAT] refactor auth middleware for OAuth2.
   [WHY] align with security policy #2345.
   [HOW] new auth code flow, backwards compatible.
2. [WHAT] prune legacy v1 API endpoints.
   [WHY] prepare for v2 release.
   [HOW] updated documentation and removed handlers.
</Context>
```
