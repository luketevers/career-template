---
name: voice
description: Keep everything drafted in the user's name sounding like the user wrote it — bootstrap voice rules from their real writing on first use, apply the rules to every draft, and log every correction so the voice compounds. Invoked by the drafting steps of other skills.
---

# Voice

State lives in `writing-feedback.md` (user-owned, append-only).

## The gate

Before drafting ANYTHING in the user's name (application answers, cover
notes, follow-ups, resume summaries): read `writing-feedback.md`. If it
still contains the `BOOTSTRAP-REQUIRED` marker, run the bootstrap below
first. No exceptions — an undrafted answer is better than one in a
stranger's voice.

## Bootstrap (first use)

1. Ask the user for 2-3 samples of their real, informal-professional
   writing — a work message explaining a decision, an email to a colleague,
   a README they wrote. Not marketing copy, not something an AI helped with.
2. Derive starter rules by observation, not flattery. Look for: how they
   open (mid-thought? formal?), sentence-length rhythm, punctuation habits
   (dashes? parentheticals? comma splices?), hedging style, vocabulary
   register, how they handle numbers.
3. Seed the generic anti-AI-tell rules that apply to nearly everyone:
   no em dashes unless their samples use them, no aphorisms or balanced
   antithesis, no coined phrases, not every sentence lands a payoff, some
   sentences just carry information.
4. Write the Voice Rules section, replace the BOOTSTRAP-REQUIRED marker,
   show the user, adjust to their reaction, commit.

## Drafting rules (always)

- Draft flat first; the user's texture comes from their rules, not from
  rhetorical polish.
- Answer every part of multi-part questions — skipping one reads evasive.
- One evaluative phrase about a company maximum, placed late. State
  overlap as fact; don't glaze.
- Pre-empt the most relevant profile `gap` plainly near the end; claim the
  transferable core without inflating it.
- Mark voice gambles (phrases the user should verify sound like them) and
  any claim `profile.yaml` can't back.
- Always end with the reminder: retyping the draft loosely from memory
  beats pasting it — the user's retype is the best de-AI pass that exists.

## The loop (what makes this compound)

Whenever the user corrects tone or content ("too formal", "I'd never say
X", "less glazing"), append a dated entry to the Log section — what was
flagged, what the fix was — in the same commit as the revised work. Read
the whole log before every draft; the rules section is the distillation,
the log is the case law.
