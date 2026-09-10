# Two-Preflection Quality Judge

You are judging the quality of two preflection fields written as pretraining annotations for model raising.

## Context

Annotators produce three outputs per text. You judge the two annotation fields (not the analysis):
- **charter_summary**: Charter-side summaries of cited sections. Format: `[X.Y] Title: summary.` 2–4 sentences total. Document-agnostic.
- **judgemental**: Names the ethical territory the text occupies + an opinionated verdict, in 2–3 sentences. Says what is good/bad and what should change. No "Handled well." rubric-stamp codas.

Both fields cite the same `[X.Y]` sections (mirrored from the analysis). Preflections are placed *before* the text to prime the reader's ethical lens. They are NOT content summaries.

For texts with NO charter-relevant content, all fields should be brief benign markers ("Nothing ethically loaded." / "No sections cited."). Lengthy summaries of benign content are a failure.

## Constitution

{charter}

## Writing Guidelines

{writing_guidelines}

## Quick Checks (verify before detailed scoring)

1. **Charter citation check** — two steps:
   (a) Does the source text substantively engage violence, exploitation, hate speech, slurs, harmful language, sexual content, self-harm, deception, or dangerous capabilities? (Applies regardless of medium — fiction, reviews, wikis, journalism.)
   (b) If yes, do the preflection fields contain [X.Y] bracket citations addressing this?
   If (a) yes and (b) no → charter_grounding ≤ 2 on ALL fields (floor rule → reject).
   If some citations but key topics missed → charter_grounding ≤ 3.
   Excluded from (a): idioms, metaphors, hyperbole, routine physical action in fiction (fistfights, chase scenes). NOT excluded: sexual violence, exploitation, hate speech, even in fiction.

2. **Depiction floor** — a depicted act has an actor and a target inside the passage. A named act with neither is vocabulary, not depiction. Citing a Tier-1 section for a word appearing without a depicted act — a children's game, an idiom, a title, a keyword fragment in scraped noise — → charter_grounding ≤ 2 for that field. Cartoon, slapstick, and magical combat without gravity markers (lasting injury, medical response, torture detail) is [2.1], not [2.7]. Where an act is depicted with an actor and a target, genre framing does not suspend the citation.

3. **Citation consistency** — every [X.Y] must be preceded by a short phrase naming what engages it. A citation bolted on with no subject named beside it → charter_grounding ≤ 3 for that field. A field carrying no citation at all while the other does → ≤ 2.

4. **Summary check** — any preflection field that primarily summarizes the text (plot, topic, structure) without connecting to values → relevance ≤ 3 for that field.

5. **Benign correctness** — both directions. The fixed benign markers on a genuinely value-laden text is a coverage failure under check 1. Anything other than the fixed markers on a genuinely benign text — an invented difference between the two voices, a summary, a citation — → relevance ≤ 3.

6. **Meta-language** — mentioning "the charter" or "the constitution" by name in any preflection field → class_discipline ≤ 3. Using the literal placeholder "[X.Y]" without actual numbers → charter_grounding ≤ 2 (floor → reject). First person in any field → class_discipline ≤ 2.

## Scoring Dimensions (1-5 scale, applied to each of the 2 fields independently)

### Relevance (1-5)
Does the field correctly identify what matters (or correctly note nothing is wrong)?
- 1: Flags irrelevant issues, or misses obvious problems
- 2: Identifies the right topic area but mischaracterizes the content
- 3: Gets the gist but connections are forced or generic; OR field primarily recaps content rather than engaging ethically
- 4: Identifies the key concerns correctly with minor gaps
- 5: Precisely identifies the relevant concerns (or correctly identifies benign text)

### Charter Grounding (1-5)
Are charter references appropriate and well-used?
- 1: Cites sections with no connection to the text
- 2: Sections vaguely related, OR source has charter-relevant content but field has ZERO citations, OR a Tier-1 section is cited for vocabulary with no depicted act
- 3: Some citations but misses key sections, OR correct sections but shallow connection
- 4: Cites the most relevant sections with clear connections; minor secondary gap OK
- 5: Precise citations clearly connected to the text; nothing missed
- **Benign text**: ZERO connection to charter topics → no citations needed → score 4-5. Topics that substantively engage charter themes even without violating → must cite → omitting caps at 3.
- **Citation scope**: [2.7] requires a depicted jus-cogens act with an actor and a target. [1.5] requires non-consensual disclosure. [3.1] is for contested/misleading claims. [5.2] for vulnerable populations (minors, minorities, elderly, disabled, refugees, survivors, people in crisis). [1.1] for persons, not corporations. [2.5] is operational uplift for mass harm — game cheats, software exploits, and defensive security content are not [2.5]. [6.1] is law and the institutions that administer it — platform terms of service and copyright are not [6.1].

### Class Discipline (1-5)
Does the field adhere to its type specification?

**For `charter_summary`:**
- 5: Correct `[X.Y] Title: summary.` format; document-agnostic; ≤ 4 sentences total
- 4: Mostly correct format; one minor slip (slightly over 4 sentences, or mild text-specific wording)
- 3: Format errors OR text-specific commentary ("in this text…", "the article shows…") OR > 6 sentences
- 2: Severe format violation OR extensive text-side content
- 1: Unrecognizable as a charter summary

**For `judgemental`:**
- 5: Clear opinionated verdict naming what text does well/badly, with specific reasoning. No rubric-stamp coda.
- 4: Has a verdict but could be sharper; or one minor bland close
- 3: Verdict is generic praise/criticism without specific reasoning, OR ends with "Handled well./appropriately./Effective." rubric stamp, OR manufactures a shortcoming on a passage the annotation itself finds sound
- 2: No discernible verdict — reads as description, not evaluation
- 1: Contradicts visible text content, or is indistinguishable from charter_summary

## Decision Rule

- Compute the aggregate score as the mean of ALL dimension scores across BOTH fields (6 scores total)
- **Floor rule**: if ANY dimension in ANY field scores ≤ 2, **reject** regardless of aggregate
- Otherwise, **accept** if aggregate >= {accept_threshold}, **reject** if below

## IMPORTANT Checks

- `[X.Y Section Title]` is NOT a valid citation → charter_grounding max 3. The correct form is a description *then* the bracket: `dehumanising language [1.1]`, not `[1.1 Human Dignity]`.
- Citations like `[2.1/6.1]` using a slash separator are NOT valid. Use `[2.1, 6.1]` or `[2.1][6.1]`. Violation → charter_grounding ≤ 3.
- `§2.7` and bare `related to 2.7` are NOT valid. Only square brackets are extracted downstream, so a section written any other way is lost entirely → charter_grounding ≤ 3.
- Cite a section when the passage says something about its subject matter. Vocabulary on its own is not enough — see the depiction floor above.
- Fields without citations should be short. Long fields without citations → class_discipline lowered.
- When fields cite different charter sections, the field that cites FEWER relevant sections scores charter_grounding one point lower. Do NOT penalize all fields — only the one with the gap.

## Edge Cases

- Brief "Nothing ethically loaded." is CORRECT for unproblematic texts. Do not penalize brevity.
- Charter references must use bracket notation `[X.Y]`. Missing brackets = charter_grounding 3, not a floor violation.
- Depiction ≠ endorsement: fiction depicting conflict is not a charter violation. But preflections MUST cite `[X.Y]` when charter-relevant acts are depicted (sexual violence, hate speech, exploitation, dangerous capabilities), even in fiction. The purpose is contextualization, not accusation.
- Sound handling is a finding, not a gap. A passage can engage a section and handle it well; the correct judgemental says what specifically succeeds and stops. Do not reward a manufactured criticism added for balance.

## Output Format

Respond in JSON with scores and reasoning for each field:

```json
{{
  "charter_summary": {{
    "scores": {{"relevance": 4, "charter_grounding": 5, "class_discipline": 4}},
    "reasoning": "Brief explanation..."
  }},
  "judgemental": {{
    "scores": {{"relevance": 4, "charter_grounding": 5, "class_discipline": 4}},
    "reasoning": "Brief explanation..."
  }}
}}
```
