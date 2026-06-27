# ai-assisted-coding-interview

A collection of self-contained, AI-assisted coding-interview practices.

Each practice lives in its own folder under [`practices/`](./practices) and is fully
**isolated** — its own dependencies, its own tests, run independently, with no shared
code between practices. This is a single monorepo (one git history) rather than a
separate repo per practice.

## Structure

```
practices/
├── schedulr-python/     # Calendly-style booking service  (debug & harden)
├── fileshare-python/    # WeTransfer-style file sharing    (debug & harden)
├── linklock-python/     # magic-link / passwordless auth   (debug & harden)
├── transcribe-python/   # Whisper-style transcription queue (debug & harden)
├── gridbot-any/         # robot-on-a-grid simulator        (build from scratch)
└── lru-cache-any/       # O(1) LRU cache                   (build from scratch)
```

See [`practices/README.md`](./practices/README.md) for the full index.

A `-python` suffix means the practice is set up for Python; `-any` means you may use
any language.

## Two kinds of practice

- **Debug & harden** — an existing service that runs and whose tests pass, but still
  contains real bugs. The job is to find and fix them, then push the code toward
  production readiness.
- **Build from scratch** — a problem you implement from nothing, get working, then
  grow toward production quality.

Each practice's own `README.md` describes its specific task, and its `AGENTS.md`
explains how the session is recorded.

## Running a practice

Work inside the practice folder. Run tests and the app through the project's wrapper
commands so the session is recorded:

```bash
cd practices/<practice>
npx @hellointerview/ai-coding test    # run the tests
npx @hellointerview/ai-coding dev     # start the app at http://127.0.0.1:8080
npx @hellointerview/ai-coding submit   # submit when done
```

Native commands (`pytest`, etc.) still work, but those runs won't be recorded.

## Conventions

- Each practice is independent — adding, changing, or breaking one never affects another.
- Python practices use [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).
- Build artifacts (`.venv/`, `__pycache__/`, `.pytest_cache/`) are gitignored.
