# Installing Resu Studio

Resu Studio is one skill, written to the open [Agent Skills](https://agentskills.io)
standard, so the same repository installs into Claude, ChatGPT and other AI tools. Every
install reads this repository, so an update here reaches all of them.

Pick the section for the tool you use. Each route below is an official channel, which
means the install is recorded and counts towards Resu Studio's listing. There is a note
at the end on what is counted and what is not.

## Claude (Cowork and Claude Code)

**From the plugin directory.** In Cowork, open **Customize**, then **Plugins**, and
search for **Resu Studio**. Click it, then **Install**. In Claude Code, run
`/plugin` and search the same directory.

**Before the directory listing is live**, add the marketplace by name instead. In
Cowork, open **Customize**, then **Plugins**, then **Add marketplace**, and enter:

```
CX-Instruments/resu-studio
```

Resu Studio then appears in your plugin browser to install.

Updates arrive in the same place: the plugin page shows an **Update** button when a new
version is out.

## ChatGPT and Codex

**From the plugin directory.** Open **Plugins** and search for **Resu Studio**, then
install it.

**Before the directory listing is live**, open **Plugins**, choose to add a plugin
marketplace, and enter `CX-Instruments/resu-studio` as the source, with `main` as the
Git ref and nothing under sparse paths.

Where ChatGPT can run the scripts, everything works. Where it cannot, the scoring, the
suggested changes and the letter still do, and the studio page and the PDF do not.

## Claude Code, Codex, Copilot, Cursor, Gemini CLI and 80 other tools

Install it with the [Skills CLI](https://github.com/vercel-labs/skills), which needs
[Node.js](https://nodejs.org):

```
npx skills add CX-Instruments/resu-studio
```

It asks which of your AI tools to install into, and whether to install for this project
or for your whole computer. To pick a tool yourself, add `-a claude-code`, `-a codex`,
`-a cursor`, `-a github-copilot` or `-a gemini-cli`.

To pick up a later version:

```
npx skills update
```

This is the route that puts Resu Studio on the [skills.sh](https://skills.sh) listing,
because the CLI counts installs.

## A downloaded file, for Claude

Download the `.plugin` file from the
[Releases page](https://github.com/CX-Instruments/resu-studio/releases), then in Cowork
open **Customize**, then **Plugins**, and use the upload option to pick the file.

A file installed this way does not update itself. To move to a newer version, download
the new `.plugin` file and upload it again.

## What each route needs

- **Nothing at all**, if you use Resu Studio inside Claude's Cowork. The work happens in
  Claude's own session and the finished documents come back to you as files.
- **Python 3 and Chrome or Edge**, if you use it in a tool that runs on your own
  computer, such as Claude Code, Codex, Copilot, Cursor or Gemini CLI. Most computers
  already have both.
- **Node.js**, only to run the Skills CLI command above.

Full details are in the [README](../README.md).

## How installs are counted

Resu Studio has no account, no server and no analytics of its own. It cannot see who
installs it or what they do with it. See [PRIVACY.md](../PRIVACY.md).

What the routes above do record:

- **The Claude and ChatGPT directories** record the install with Anthropic and OpenAI,
  the same as any other listed plugin.
- **The Skills CLI** counts installs anonymously, which is how skills are ranked on
  skills.sh. Set `DISABLE_TELEMETRY=1` before the command to turn that off.
- **The Releases page** counts how many times the `.plugin` file has been downloaded.

Copying the files by hand, or cloning the repository, works and is allowed by the
licence, and none of it is counted anywhere.
