# Resu Studio

Tailor a CV and a written application to one job advertisement, honestly.

It reads the advertisement and your CV, scores one against the other, and shows you
where you stand before it changes a word. Every proposed change arrives as three
things, the current text, the suggested text, and the reason, and you accept or
reject them one at a time. Then it rescores, so you can see what your decisions
actually moved.

The finished CV and cover letter print to PDF exactly as the studio shows them: the
same colours, the same layout, the same skills graphics, the same typefaces, and the
text stays text so an applicant tracking system can still read it.

## What it will not do

- It will not invent experience, inflate a level, or turn a duty into an achievement
  you did not describe. Every line traces back to something you wrote.
- It will not quietly hand you a document that differs from what you approved. If a
  typeface cannot be loaded, it deletes the PDF and says which one, rather than
  substituting a face with different metrics and re-flowing every line.
- It will not write over an earlier application. Re-rendering the same document
  replaces it, which is what you want when trying skins. A different advertisement
  keeps the earlier file under a dated name, and the employer is in the filename, so
  two applications for the same job title at different employers stay apart.

## Getting started

Say what you are applying for and give it your CV. It will ask for the job pack if
the advertisement points at one, and it will ask how deep to score before it starts,
because that is the longest part of the job and the decision is yours.

## Where your files go

Your history and your finished documents do **not** live inside the plugin. They live
in `.resu-studio` in your home folder, so a plugin update cannot delete them. That is
the default and it needs no setting up.

```
python3 scripts/paths.py       where your folder is, and why
python3 scripts/documents.py   what you have produced, and for which advertisement
```

To choose the folder yourself, put a single line, the path you want, in
`.resu-studio/location` in your home folder. The older `data-location.txt` beside
`SKILL.md` still works, and the first time it is used it is copied out to
`.resu-studio/location`, so the next update cannot take the pointer with it.

Write the path the way the machine doing the work sees it. It starts with a `/` and
has no drive letter and no backslashes. A Windows path like `D:\Users\Jane\CVs` is
refused with a message saying so, and where it can, the message names the folder on
the working machine that looks like the one you meant.

If you used this before it stopped keeping files inside the plugin, your old folder is
copied out to the new one the first time it runs. Nothing is moved, nothing already in
the new folder is written over, and it tells you what it did. It happens once.

Your CV, your facts ledger and every PDF you have already produced survive every new
advertisement. Only the job-specific work is replaced, and you are told before it is.

## What you need to install

Nothing.

You will not be asked to run a command, set a path, or install anything. The work
happens where Claude is running, and the finished documents come back to you as files.
You should never have to know what any of it is written in.

The typefaces are carried inside the plugin, so your documents print the same whether
or not the machine doing the printing has ever been online. The studio you look at on
screen carries the same ones, so the page breaks you see are the page breaks you get.

## The seven phases

1. **Sources.** The advertisement and your CV, captured verbatim
2. **Atomise.** Your history into a facts ledger, the advertisement into an asks ledger
3. **Score.** One against the other, before anything is changed
4. **Propose.** Current text, suggested text, reason
5. **Decide.** You accept or reject, one at a time
6. **Assemble.** The tailored CV, then rescore and show the movement
7. **The cover letter.** One page, in your voice

The facts ledger is built once and reused. A second advertisement reads it rather
than asking you for your CV again.
