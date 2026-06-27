# lru-cache

lru-cache is a cache you build from scratch. A cache holds a fixed number of key/value pairs, and the rule that makes it interesting is what happens when it fills up. You read a value by its key, you write a key/value pair, and every time you touch an entry, reading it or writing it, that entry becomes the freshest one. When the cache is full and a brand new key comes in, the entry nobody has touched in the longest time gets dropped to make room. The catch is that both the read and the write have to stay O(1), so the structure underneath has to do real work.

## Your task

You have two jobs.

1. **Build the core and get it working.** A cache with a fixed capacity, a way to read a value by its key, and a way to insert or update a key/value pair. Reading or writing an entry makes it the most recently used. When an insert would push the cache past its capacity, evict the least recently used entry first. Both the read and the write need to run in O(1). This part is the floor, and most submissions get here with or without an AI.
2. **Push it further toward production readiness.** The interesting part is where you go from the basics. You won't get it fully production-ready in the time you have, and we don't expect you to. Treat this like real code you'd be happy to hand a teammate, decide what would matter most for putting it in front of real users, and push it as far as you can on the things you pick. What "production ready" means here, and how far you grow the functionality beyond the core, is yours to define. Be ready to walk through your plan and defend why you tackled what you did first.
  One thing that's *not* in scope is deployment. We're not hosting this anywhere, so skip Dockerfiles, CI, and infra and focus on the code itself.

We care more about your judgment on what to tackle first than about a long list of half-finished features.

## Time

Aim for **30 minutes**. This is practice, so going over is fine, but your submission records exactly how long you took, and that time factors into the evaluation.

## Tools

Use whatever you'd use day to day. AI assistants (Cursor, Copilot, ChatGPT, Claude), search, library docs, Stack Overflow. Anything goes. We want to see how you actually work, not how you perform without your normal tooling.

## Building it

This repo is intentionally empty except for this README, so you're starting from a blank page. Set it up in whatever language and framework you like, using your own toolchain (your own package manager, test runner, and build commands).

When you're done, run `npx @hellointerview/ai-coding submit` to submit your code.

## Git

This is a regular git repo, so use git however you like. Commit as you go, make branches, do whatever fits how you normally work. It won't get in the way and we're not going to fight your workflow.

The one thing to know is there's nowhere to push. When you run `npx @hellointerview/ai-coding submit` we bundle up your work and submit it for you, so commits are just for your own benefit, not how you turn the exercise in. Your full set of changes is included either way, whether you committed them or not.
