# transcribe

transcribe is a small Whisper-style transcription job queue. You POST an audio URL, a background worker downloads the file, runs transcription on it, and stores the text, and you poll the job to get the result back when it's done. The three endpoints that drive it are listed below.

It's been running in low-traffic production for a few months and all the tests pass. That doesn't mean it's correct, and it definitely doesn't mean it's ready for real load.

## Your task

You have two jobs.

1. **Find and fix the bugs.** There are a handful of real bugs in here. The existing tests pass, so they won't point you at them — read the code carefully, exercise the endpoints, and fix what actually matters. Be ready to explain what you found, what you fixed, and anything you chose to leave alone.

2. **Push it toward production readiness.** Right now it's a prototype that happens to run. You won't make it fully production-ready in an hour, and we don't expect you to. Think about what it would actually take to put this in front of real users at real volume, decide what matters most, and get as far as you can on the things you pick. What "production ready" means here is yours to define. Be ready to walk through your plan and defend why you tackled what you did first.

   One thing that's *not* in scope: deployment. We're not actually hosting this anywhere, so skip Dockerfiles, CI, and infrastructure work and focus on the code itself.

We care more about your judgment on what to tackle first than about a long list of half-finished changes.

## Time

Aim for **60 minutes**. This is practice, so going over is fine — but your submission records exactly how long you took, and that time factors into the evaluation.

## Tools

Use whatever you'd use day to day. AI assistants (Cursor, Copilot, ChatGPT, Claude), search, library docs, Stack Overflow — anything goes. We want to see how you actually work, not how you perform without your normal tooling.

## API

- `POST /jobs` — submit a transcription job (body: `{"audio_url": "...", "language": "en"}`)
- `GET /jobs/<id>` — get a job's status and result if done
- `GET /jobs` — list recent jobs

## Running it

The runtime is already set up by `npx @hellointerview/ai-coding start`. From this folder:

    npx @hellointerview/ai-coding test    # run the tests
    npx @hellointerview/ai-coding dev     # start the app at http://127.0.0.1:8080

`npx @hellointerview/ai-coding dev` automatically picks another port if 8080 is taken. When you're done, run `npx @hellointerview/ai-coding submit`.

## Git

This is a regular git repo, so use git however you like. Commit as you go, make branches, do whatever fits how you normally work. It won't get in the way and we're not going to fight your workflow.

The one thing to know is there's nowhere to push. When you run `npx @hellointerview/ai-coding submit` we bundle up your work and submit it for you, so commits are just for your own benefit, not how you turn the exercise in. Your full set of changes is included either way, whether you committed them or not.
