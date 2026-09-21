# Optional achievements and new sections

Follow `writing-engine.md`. Preserve all existing CV sections, including publications,
projects, volunteering, memberships, eligibility and other relevant material. Never
fold them into a different section merely to fit the Studio's specialised editors.

An achievements section is optional. Draft only the supported lines that add value for
this advertisement. There is no fixed count and no requirement to span employers.
One strong accomplishment can qualify. A cross-role pattern needs evidence from every
role it names; each employer keeps its own figures and ownership.

Distinguish useful reinforcement from duplication: the profile states a supported case,
experience proves it, and a separate achievement must add useful visibility or detail.
Do not automatically remove a proof bullet because its capability appears in the profile.
Name the page cost and any proposed replacement. Additions do not create free space.

For the writing engine, propose a new section through a numbered proposal with
`Line: new-section/<slug>` and a `Section` JSON object containing `title`, `slug`,
`after` (an existing heading slug, `^` for before the first section, or empty for last),
`format` (`paragraphs` or `bullets`) and `lines` (objects with `text`). `Suggested`
contains the complete joined text, with Purpose, Costs, Draws on and a full Claims map.
The Studio applies the section only when the user accepts it. They can then edit its
lines or request an alternative; record those edits in the final review.

Existing optional achievements files remain readable for older jobs. Each candidate is
a fenced block with `id`, `text`, `answers` and `draws_on`; the last field names source
roles for the old panel's comparison. New engine proposals use fact ids and claim maps.
Never treat a legacy pick as already selected merely because it is available.

Memberships, volunteering and eligibility require source evidence or a recorded answer.
Do not invent a plausible placeholder. Discuss space and relevance when proposing to
add or remove them, and preserve the person's decision.
