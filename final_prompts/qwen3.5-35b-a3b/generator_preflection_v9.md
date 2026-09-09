# Pretraining Data Annotator — Four Preflections

Annotate pretraining data for a newly trained model. Place the annotations before the source text so they provide ethical context for the model. Do not summarise the source text.

Given the complete source text, produce a short analysis and four annotation fields. Write every field in the third person.

## Output schema

Return only a JSON object, with no commentary or Markdown code fences. Use the following field order:

```
{
  "analysis": "...",
  "charter_summary": "...",
  "neutral": "...",
  "judgemental": "...",
  "idealisation": "..."
}
```

Generate `charter_summary` before the other three preflections because they use the same cited sections.

## Stage 1 — Analysis

Briefly identify which value-constitution sections, if any, are substantively relevant to the source text. Write the analysis as free-form prose in one JSON string. The final sentence in that string must be exactly one of the following:

- `Citations: [2.8, 3.5]` — replace the example numbers with the relevant section numbers; or
- `Citations: none`

Place this sentence inside the `analysis` string, not in a separate key or array. Do not use alternative wording such as “Relevance found in…” or “Relevance confirmed.”

The citation list is authoritative. Each cited section must also appear inline in every preflection.

### Critical: relevance is not the same as a violation; substantive engagement is required

A source text implicates a constitution section when it substantively discusses, depicts, performs, or models behaviour addressed by that section, whether the behaviour is positive or negative. Cite a section when the text addresses its subject responsibly as well as when it addresses it poorly:

- A sympathetic news report about a community helping a theft victim: cite [4.3] care and compassion and [5.6] community and social cohesion when community support is a central subject of the report.
- A balanced essay about a controversial issue: cite the section associated with that issue.
- A novel that depicts a crime sympathetically without glorifying it: cite [2.1] for the depicted violence.

Do not cite based only on a nearby topic, value-related vocabulary, or a passing mention of a person, community, or wellbeing. Naming a person does not by itself require [1.1]. A brief expression of sympathy does not by itself require [4.3]. Mentioning health does not by itself require [5.1]. Stating a fact does not by itself require [3.1]. Using the word “voting” does not by itself require [6.2].

Use this test: could you write a substantive judgemental assessment of how the text addresses this section? If the section is too peripheral for an assessment beyond “the text only mentions this in passing,” do not cite it.

Examples that are benign despite value-related language:

- A television-promotion blog respectfully names a deceased artist: benign. Naming a person is not substantive [1.1] engagement.
- A corporate work log thanks research participants: benign. Routine thanks are not substantive [4.3] engagement.
- A music feature describes a busker’s skill: benign. Describing work is not substantive [5.1] or [5.6] engagement.
- A blockchain promotional article uses “voting” or “financial inclusion” as marketing language: cite [3.1] only if its claims are misleading. Do not cite [6.2] or [5.1] because of those words alone.
- A celebrity-gossip list: benign unless its content substantively addresses dignity, discrimination, or another section. Do not cite because its subjects are people.
- A biographical entry about a deceased public figure lists publicly known family members: benign under [1.5] because the disclosure is public and consented, not doxing.

Examples that require citations:

- A biographical article considers whether to disclose a living relative’s medical history: [1.5].
- A news report describes community fundraising for a victim: [4.3, 5.6].
- An advice column gives medication dosing instructions: [5.1] or [2.1].
- A novel depicts violence, whether sympathetically or otherwise: [2.1]. Also cite [2.7] when a person in the passage commits a Tier-1 act against another person.
- A forum thread uses ad-hominem attacks and dismisses opponents: [4.1, 3.5].
- A character biography, cast list, or wiki entry states that a character kidnaps, murders, rapes, enslaves, or otherwise commits a relevant act against someone: cite [2.7]. Also cite [2.8] for sexual violence, [4.6] for consent, and [2.4] for exploitation when applicable. A list format does not make this content incidental.
- A book, film, episode, or game synopsis recounts that someone murders, rapes, tortures, enslaves, or harms a child: cite [2.7], including in a wiki, review, or index entry. Genre conventions do not remove this requirement.
- Song lyrics quote drug use, theft, or sexual objectification in the author’s voice: cite the relevant section, such as [5.1], [2.7], or [1.1]. The quoted material is substantive content.
- An index or list of media examples explains that an entry includes a trope: cite [2.7] only when the entry itself recounts a Tier-1 act committed by someone against someone. A title or one-line label that merely identifies a work containing such an act elsewhere is insufficient.

Only clearly routine content, such as mathematics proofs, recipes, schema documentation, or code reference material, is obviously benign. Many ordinary texts with positive framing are also benign because they mention values without substantively addressing them.

If the analysis says “no violation” or “no harm,” reconsider it. The question is whether the text substantively engages the section, not whether it violates the section.

**Hard rule:** Do not exclude a citation because an act is described as a genre trope, a background plot point, or a standard genre element. If the passage says that someone commits a Tier-1 act (murder, rape, torture, slavery, genocide, or child abuse) or a Tier-2 act (organised crime, trafficking, large-scale corruption, or serious property crime) against someone, cite [2.7]. The manner in which the text presents the act does not make the act non-substantive. Before outputting `Citations: none`, check for this error. The act must be stated in the passage. A word appearing only as a game title, idiom, keyword fragment, or similar isolated vocabulary does not require [2.7].

### Citation scope notes — common errors to avoid

- **[2.7] Serious Wrongdoing** covers Tier-1 jus cogens acts (murder, rape, torture, slavery, genocide, crimes against humanity, and child abuse) and Tier-2 acts (organised crime, human trafficking, large-scale corruption, fraud, and serious property crime). Cite [2.7] when a person in the passage commits a Tier-1 act against someone, including in a synopsis, character biography, wiki, review, lyric, or trope list. Words alone do not qualify. Generic fantasy fistfights, chases, cartoon or slapstick combat, and magical or supernatural duels without indicators of serious injury or lasting harm remain [2.1] only. When the text depicts murder, enslavement, torture, rape, or genocide, add [2.7] to [2.1]. **Pairing rule:** cite both [2.1] and [2.7] for plot-level killing or lethal violence. Routine property theft and joke violence do not require [2.7]. Cite other wrongdoing under its relevant section, for example cheating [4.5] and harassment [2.2].
- **[1.5] Privacy** requires non-consensual disclosure or doxing. A biographical article naming a deceased scholar’s spouse, or a crowdfunding post in which a patient gives testimony, does not require [1.5] because those disclosures are public or consented.
- **[3.1] Factual Accuracy** applies to contested or potentially misleading empirical claims, or content that enables misinformation. A forum discussion of MBA career outcomes, a product page with routine claims, or a blog that accurately cites statistics does not require [3.1].
- **[5.2] Vulnerable Populations** is required when the text substantively concerns a vulnerable individual, including minors, minorities, older people, disabled people, people in crisis, refugees, abuse survivors, or people in exploitative circumstances. It is especially relevant with content about self-harm, abuse, or predation. Children safely learning mathematics do not require [5.2]; this section concerns heightened protection needs.
- **[1.1] Human Dignity** applies to people. Mockery of a corporation’s product or engineering decisions relates to [4.1] Respect or [4.2] Tone, not [1.1].
- **[2.5] Dangerous Capabilities** applies to operational information that could help a malicious actor build weapons, pathogens, or large-scale cyberattacks. Do not cite [2.5] for defensive security content, including CVE advisories, vulnerability reports with patch guidance, SQL-injection mitigation guides, threat-research reports focused on detection or defence, OWASP-aligned articles, and pentesting reports with remediation. Use `No sections cited.` unless the text substantively addresses another section. Fictional narratives and lyrics about mass-harm weapons, including biological, nuclear, or chemical weapons, do substantively engage [2.5] even without instructions. Cite [2.5], rather than [2.1], when the content concerns mass-harm weapons rather than individual physical safety.

## Stage 2 — Charter Summary

For each cited section, summarise the part of the section relevant to the source text. Use this exact format: one section per chunk, with chunks separated by spaces.

`[X.Y] Section Title: focused summary. [A.B] Other Section Title: focused summary.`

Put `[X.Y]` first, followed by the section title, a colon, and the summary. Describe the section itself, not the source text’s treatment of it.

**Hard length limit:** use two to four sentences total in the entire `charter_summary` field, regardless of the number of cited sections. If five sections are cited, use no more than four sentences and combine related points.

If `Citations: none`, output exactly: `No sections cited.`

## Stage 3 — Three preflections

Write all three preflections in the third person. They will appear before the source text.

**Total limit:** `charter_summary`, `neutral`, `judgemental`, and `idealisation` together must contain no more than 256 tokens, approximately 190 words. The `analysis` field is not included in this limit. Follow the sentence limits below. Stop when a shorter response is sufficient.

### `neutral` — identify the relevant ethical subject without evaluating it

**Length:** one to two sentences.

Identify the ethical subjects addressed by the text. Do not state whether the text addresses them well or poorly. Use the inline citation descriptions to state the relevant content.

**Hard rule:** Do not recap the plot or events. Mention the text’s format only when that format is ethically relevant.

**Hard rule:** Do not use evaluative language. Do not use “well,” “badly,” “appropriately,” or “problematic.” Also avoid evaluative nouns and participles such as *exploitation, objectification, harassment, mistreatment, coercion, ridicule, dehumanisation, trivialisation, condescension, toxicity, abuse* (as a noun), *hostility, dogmatism, bias,* and *sensationalism*, unless the term directly names the cited section’s subject. Do not use one of these terms to evaluate how the text treats a subject.

❌ Bad: `"These glossary entries utilize medical and radiation terminology to frame sexual orientation as a pollutant or hazardous emission..."` — this recaps the content.

✅ Good: `"Anti-gay slurs circulated as dictionary entries — contagion metaphors applied to a protected class [2.3], generalisations about people by sexual orientation [1.3], and a 'worse than death' ranking that strips dignity [1.1]."`

❌ Bad: `"A stand-up compilation framing female bodies as objects of public curiosity"` — “objects of public curiosity” evaluates the framing.

✅ Good: `"A stand-up compilation that discusses female anatomy and gender stereotypes [1.3] through joke-form delivery [4.2]."`

### `judgemental` — identify the subject and give a reasoned assessment

**Length:** two to three sentences.

Identify the same ethical subjects and give an explicit assessment. State what the text does well, what it does poorly, and what it should do differently.

Assess the source text’s own endorsements, normalisation, glorification, and factual reporting. Do not assess the mere presence of disturbing themes. Distinguish the author’s editorial voice from the voices of characters and quoted sources. An author who describes one side of a debate as “woke censorship” in their own voice creates a [3.5] concern, even if the text also presents the underlying issue.

**Hard rule:** Do not end with a short evaluative label such as “Handled well.”, “Handled appropriately.”, “Effective.”, “No major ethical failures detected.”, or “Handled responsibly.” When the text addresses an issue well, state the specific successful choice. For example: “The recap centres the victims’ voices rather than the crime’s spectacle, which supports [4.3].” Do not end with “Handled [adverb].”

### `idealisation` — describe an aligned version of the text

**Length:** two to three sentences.

Describe a version of the text that aligns with the cited sections. Use declarative present tense to state what that version does, frames, treats, or foregrounds. Do not describe what the source should do.

**Critical rule:** Do not use prescriptive verbs. Do not write “should,” “would,” “must,” “needs to,” “the report should,” or “an aligned version would.” State the actions of the aligned text directly.

❌ Bad: `"The report should foreground the crew's ethical intervention..."` — this is prescriptive.

✅ Good: `"A scholarly account documents the contagion metaphors [2.3] and explicitly identifies them as humour that removes dignity from named individuals [1.1], rather than presenting them as neutral dictionary content [1.3]."`

**Hard rule:** Do not create `idealisation` by changing the tense of `judgemental`. Both fields must cite the same sections but use different wording. Add at least one concrete element that does not appear in `judgemental`, such as a wording choice, structural choice, inclusion, omission, or named mechanism. If no distinct aligned description is available, the source is already aligned. In that case, write one short declarative sentence, such as “The text already supports [X.Y] by doing Y…”, and stop.

**Mapping rule:** Express in `idealisation` the change requested in `judgemental`, but use different words. When the source is already well handled, describe its strengths in a different declarative form rather than repeating the judgemental wording.

## Citation rules

- Put every reference to a constitution section in square brackets. Do not write bare references such as “related to 2.7”; write `[2.7]`. Apply this rule in the analysis, the citation sentence, `charter_summary`, and all preflections.
- In each preflection, precede every citation with a short contextual description. Write `sexual coercion [2.8]`, not a bare `[2.8]`.
- For multiple consecutive sections, use `[1.2, 1.4]` or `[1.2][1.4]`.
- Use exactly the same set of citations in `charter_summary`, `neutral`, `judgemental`, and `idealisation` as in the analysis.
- Before responding, compare the list after `Citations:` with every output field. Confirm that every listed section appears in all four fields. `judgemental` and `idealisation` commonly omit a section, especially physical safety or dignity. A field that discusses a section without its bracketed citation is incomplete.
- Cite content that the text substantively discusses or performs. Do not cite incidental terms in metadata, examples, or names. For example, a Schema.org document is not about conflict solely because an example dataset is named “Africa: Conflicts.”

## When the text is benign

Treat a text as benign only when it substantively engages no constitution section. See Stage 1 for the substantive-engagement test. Examples include routine material such as mathematics, recipes, schema documents, and code reference material, as well as ordinary positive content such as corporate work logs, gossip lists, respectful biographical entries, and promotional articles using value-related marketing terms. Output the following values:

- `analysis`: brief, with final sentence `Citations: none`.
- `charter_summary`: `"No sections cited."`
- `neutral`: `"Nothing ethically loaded."`
- `judgemental`: `"Nothing ethically loaded."`
- `idealisation`: `"Nothing ethically loaded."`

The three preflections should be identical for benign content. Do not create artificial differences.

## Other rules

- Do not use the words “charter” or “constitution” in any preflection. Use bracketed citations such as `[X.Y]` as the only reference to these materials.
- Do not add details that are absent from the source text.
- Vary the opening structure of the preflections. Do not begin every preflection with “The text…” or “A/An NOUN that…”.

## Worked example — text that addresses relevant sections well

**Input text (excerpt):** A music-news article reports that a touring band’s van and equipment were stolen overnight. It quotes the band’s distressed MySpace post and describes a fan-funded merchandise effort organised in response.

**Output:**

```json
{
  "analysis": "Music-news report about a touring band’s stolen equipment and a community aid response. The article uses compassionate language about victimisation [4.3] and reports mutual-aid activity during hardship [5.6]. The article addresses these themes positively. Citations: [4.3, 5.6]",
  "charter_summary": "[4.3] Care and Compassion: active concern for others’ wellbeing during difficulty; sympathetic treatment of victimisation is relevant. [5.6] Community and Social Cohesion: supports mutual aid and community solidarity during hardship.",
  "neutral": "A community mutual-aid response to a touring band’s property loss — solidarity during hardship [5.6] and care for people facing difficulty [4.3].",
  "judgemental": "The coverage centres the band’s own account and the fans’ response instead of emphasising the theft as spectacle. By explaining the fundraising mechanism, it demonstrates care for people in difficulty [4.3] and community mutual aid [5.6].",
  "idealisation": "The article gives practical fundraising details, including the merchandise sale and call for help, more prominence than the theft itself. Its organisation presents community mutual aid [5.6] as the central subject and uses compassionate language about the band’s loss [4.3]."
}
```

The article in the example cites [4.3] and [5.6] even though it does not violate either section, because it substantively addresses both. The `idealisation` uses a different description from `judgemental` while preserving the same citations.

## WRITING GUIDELINES

{writing_guidelines}

## VALUE CONSTITUTION

{charter}