# gridbot

gridbot is a robot simulator you build from scratch. Picture a rectangular room laid out as a grid. Some cells are open, some are blocked by obstacles, and a robot sits somewhere on the floor facing one of four directions. A user drives that robot around with movement commands like turn and step forward, and the simulator tracks where the robot is, keeps it from walking through a wall or an obstacle or off the edge of the room, and can report its state at any point.

## Your task

You have two jobs.

1. **Build the core and get it working.** A room (a grid with some obstacles), a robot (a position and the direction it's facing), and the commands to drive it, at minimum turn left, turn right, and move one cell forward. Enforce the rules of the room so the robot can't move onto an obstacle, off the grid, or into an invalid state, and give the user a way to feed commands in and see where the robot ended up. This part is the floor, and most submissions get here with or without an AI.
2. **Push it further toward production readiness.** The interesting part is where you go from the basics. You won't get it fully production-ready in the time you have, and we don't expect you to. Treat this like real code you'd be happy to hand a teammate, decide what would matter most for putting it in front of real users, and push it as far as you can on the things you pick. What "production ready" means here, and how far you grow the functionality beyond the core, is yours to define. Be ready to walk through your plan and defend why you tackled what you did first.
  One thing that's *not* in scope is deployment. We're not hosting this anywhere, so skip Dockerfiles, CI, and infra and focus on the code itself.

We care more about your judgment on what to tackle first than about a long list of half-finished features.

## Time

Aim for **45 minutes**. This is practice, so going over is fine, but your submission records exactly how long you took, and that time factors into the evaluation.

## Tools

Use whatever you'd use day to day. AI assistants (Cursor, Copilot, ChatGPT, Claude), search, library docs, Stack Overflow. Anything goes. We want to see how you actually work, not how you perform without your normal tooling.

## Building it

This repo is intentionally empty except for this README, so you're starting from a blank page. Set it up in whatever language and framework you like, using your own toolchain (your own package manager, test runner, and build commands).

When you're done, run `npx @hellointerview/ai-coding submit` to submit your code.

## Git

This is a regular git repo, so use git however you like. Commit as you go, make branches, do whatever fits how you normally work. It won't get in the way and we're not going to fight your workflow.

The one thing to know is there's nowhere to push. When you run `npx @hellointerview/ai-coding submit` we bundle up your work and submit it for you, so commits are just for your own benefit, not how you turn the exercise in. Your full set of changes is included either way, whether you committed them or not.
