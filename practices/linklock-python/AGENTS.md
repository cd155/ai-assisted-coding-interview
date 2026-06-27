# Working in this repo

This is a take-home coding exercise. Work however you normally would, AI tooling included. The goal is to see how the work actually gets done.

One thing matters for how the session is recorded. Run the tests and the app through the project's wrapper commands, not the language's native ones:

```
npx @hellointerview/ai-coding test    # run the tests
npx @hellointerview/ai-coding dev     # start the app at http://127.0.0.1:8080
```

Use these instead of invoking the native commands directly (`pytest`, `npm test`, `go test`, `dotnet test`, `mvn test`, or starting the server by hand). The wrapper runs the same underlying toolchain and streams the same output. It just records the run as part of the submission so the work can be reviewed afterward. Native commands still work, but those runs won't show up in the session.

When you're done:

```
npx @hellointerview/ai-coding submit
```
