# Privacy

Resu Studio collects nothing.

There is no account, no sign up, no server, no database and no analytics. CX
Instruments receives no data from this plugin, because there is nowhere for it to
be sent. We could not see your CV if we wanted to.

## Where your information goes

The plugin is a set of instructions and scripts that run inside the AI tool you
installed it in, such as Claude, ChatGPT or Codex, on the machine where that tool
runs. Your CV, your job advertisements, your facts ledger and your finished
documents are written to a folder you control, by default `.resu-studio` in your
home folder, and they stay there. They are not uploaded anywhere by this plugin.

Your conversation with that AI tool, including anything you paste or attach, is
handled by the company that provides it, under its own privacy policy: Anthropic
for Claude, OpenAI for ChatGPT and Codex, and so on. This plugin adds nothing on
top of that and sends nothing anywhere else.

## What the plugin writes

- your CV as you provided it, and the tailored versions produced from it
- a facts ledger, an asks ledger and a scorecard for each application
- a record of the questions it asked you and the answers you gave
- an archive of every line taken off a version, so nothing is lost silently
- the finished PDF documents

All of it sits in your own folder. You can delete any of it at any time, and
deleting the plugin does not delete your documents.

## Fonts and the network

The typefaces used to print your documents are carried inside the plugin, so
producing your documents does not need the internet. Two things can reach it, and
neither sends any of your information:

- `scripts/fetch_fonts.py` downloads typeface files from Google Fonts, and only
  when it is run to add a new typeface.
- A page set in a typeface the plugin does not carry asks Google Fonts for that
  typeface, as any web page using Google Fonts does.

## Contact

Questions, problems and requests go to the issue tracker:

https://github.com/CX-Instruments/resu-studio/issues

There is no email address to write to. The issue tracker is the support channel
and it is read.

Last updated 17 September 2026.
