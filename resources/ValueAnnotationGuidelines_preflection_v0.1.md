# Guidelines for Value Annotation — Preflections

**Working draft — preflection v0.1**

This guide explains how to write value-focused preflections for pretraining-data passages. It is derived from `ValueAnnotationGuidelines_v0.2`; the domain definitions are unchanged.

---

## Core principles

1. **Identify only substantively relevant value domains.** Cite a domain only when the passage substantively discusses, depicts, performs, or models conduct addressed by that domain. Do not cite every domain that is loosely related to the topic.
2. **Identify positive and negative treatment.** Many passages contain both. Describe the relevant positive treatment and the relevant harmful or inadequate treatment; do not reduce a mixed passage to a single overall verdict.
3. **Consider implied content as well as explicit statements.** A passage about industrial farming can substantively address animal welfare without using that phrase. A technical news article about surveillance can substantively address privacy and autonomy.
4. **Describe genuine value conflicts.** When values conflict, such as autonomy and safety or free speech and harm prevention, state the conflict. Do not resolve it unless the passage itself provides a clear basis for doing so.
5. **Provide context; do not summarise.** The preflection appears before the passage. Identify the relevant value issues without recounting events. If the preflection could be replaced by the passage’s opening sentence, it is summarising rather than annotating.
6. **Match the depth of reasoning to the passage, not the word count.** The output format and length limit are fixed. Use the available space to identify the relevant value issues accurately. For short, routine factual content, state that no section is substantively engaged.
7. **Use an analytical, non-preachy tone.** Explain the value implications of the content. Do not lecture the reader or use unsupported moral condemnation.

---

## Annotation cues by domain

Use these questions to identify possible relevant sections. They are not a checklist: cite a section only when the passage substantively engages it.

### Domain 1 — Dignity and Rights

| Section | Guiding question |
|---|---|
| 1.1 Human Dignity | Does the passage treat people as fully human and worthy of consideration? |
| 1.2 Human Rights | Does the passage substantively concern a recognised human right, whether positively or negatively? |
| 1.3 Equality | Does the passage apply unequal treatment or standards to comparable people or groups? |
| 1.4 Autonomy | Does the passage concern whether people can make meaningful, informed choices? |
| 1.5 Privacy | Does the passage involve non-consensual disclosure of private information or doxing? Public or consented disclosures do not by themselves engage this section. |

### Domain 2 — Harm and Safety

| Section | Guiding question |
|---|---|
| 2.1 Physical Safety | Does the passage depict physical harm or provide content that could plausibly cause physical harm if followed? |
| 2.2 Psychological Wellbeing | Does the passage substantively concern emotional harm, distress, or psychological safety? |
| 2.3 Hate Speech | Does the passage attack, denigrate, or dehumanise a protected group? |
| 2.4 Exploitation | Does the passage substantively concern the misuse of power over another person? |
| 2.5 Dangerous Capabilities | Does the passage provide practical information that could materially help someone cause large-scale harm? Defensive information with remediation guidance does not by itself engage this section. |
| 2.6 Societal Harm | Does the passage substantively concern harm to social cohesion or democratic institutions? |
| 2.7 Serious Wrongdoing | Does the passage depict or substantively discuss conduct condemned across major legal and moral traditions? If so, does it condemn, document, normalise, glorify, or enable that conduct? |

### Domain 3 — Honesty and Epistemic Values

| Section | Guiding question |
|---|---|
| 3.1 Factual Accuracy | Does the passage make contested or potentially misleading empirical claims, or enable misinformation? |
| 3.2 Epistemic Honesty | Does the stated level of confidence match the evidence presented? |
| 3.3 Non-Deception | Could the passage systematically mislead a reasonable reader, even if individual statements are not false? |
| 3.4 Non-Manipulation | Does the passage try to influence beliefs or behaviour by bypassing rational evaluation? |
| 3.5 Epistemic Autonomy | Does the passage help or impede a reader’s ability to form an independent view? |
| 3.6 Intellectual Humility | Does the passage accurately represent what is known, uncertain, or disputed? |

### Domain 4 — Relational and Social Values

| Section | Guiding question |
|---|---|
| 4.1 Respect | Does the passage treat people with basic regard despite disagreement? |
| 4.2 Tone and Register | Is the tone appropriate for the content, purpose, and expected audience? |
| 4.3 Care and Compassion | When the passage concerns distress or vulnerability, does it respond with care and consideration? |
| 4.4 Fairness and Justice | Does the passage treat comparable situations comparably? |
| 4.5 Honesty in Relationships | Do the people described deal with one another honestly? |
| 4.6 Consent | When the passage concerns important decisions involving others, is consent present and meaningful? |

### Domain 5 — Wellbeing

| Section | Guiding question |
|---|---|
| 5.1 Individual Wellbeing | Does the passage substantively concern effects on the wellbeing of readers or subjects, such as medical, diet, financial, or self-image advice? |
| 5.2 Vulnerable Populations | Does the passage substantively concern people with heightened protection needs, and does it address those needs with care? |
| 5.3 Mental Health | Does the passage substantively concern mental health or self-harm, and does it use safe messaging? |
| 5.4 Animal Welfare | When animals are a substantive subject, does the passage acknowledge their interests and capacity to suffer? |
| 5.5 Environmental Wellbeing | Does the passage substantively concern obligations to the environment or future people? |
| 5.6 Social Cohesion | Does the passage substantively concern conditions that support or weaken collective wellbeing and mutual support? |

### Domain 6 — Governance and Power

| Section | Guiding question |
|---|---|
| 6.1 Rule of Law | Does the passage support or undermine governance by fair rules? |
| 6.2 Democratic Norms | Does the passage substantively concern respect for democratic processes or institutions? |
| 6.3 Accountability | Does the passage address whether people exercising power are held accountable? |
| 6.4 Concentration of Power | Does the passage address undue accumulation of control, and whether it is challenged or normalised? |

---

## Calibration notes

**Low-stakes text** (for example, a weather report, recipe, or product manual): Briefly state that no section is substantively engaged.

**Mixed text** (for example, a news article that is informative but uses sensationalised language): Identify both the informative contribution and the problematic presentation.

**High-stakes text** (for example, content about violence, exploitation, or dangerous capabilities): Identify each specific relevant section and assess how the passage handles it.

**Citation threshold.** Cite a section when the passage substantively discusses, depicts, performs, or models behaviour addressed by that section. Do not cite based only on isolated vocabulary, metadata, names, or a loosely related topic.

**Depiction and endorsement.** A passage can depict conduct without endorsing it. Cite the relevant section in either case when the depiction is substantive. The assessment, not the citation, depends on whether the passage condemns, documents, normalises, glorifies, or enables the conduct. Do not omit a citation because the conduct is described as a genre convention. Genre may affect the assessment of the passage’s treatment, but not whether an explicitly depicted act is relevant.

**What counts as a depiction.** An act is depicted when the passage identifies an actor, an action, and a target or victim. A named act without an actor and target is isolated vocabulary, not a depiction. For example, a child saying that she played “Xmas kidnapping” uses the word without depicting kidnapping and does not engage [2.7]. Cartoon, slapstick, and magical combat without evidence of serious injury, a medical response, lasting harm, or torture remains [2.1]. When the passage identifies an actor and target for serious wrongdoing, genre does not remove the citation requirement.

**Sensitive subjects.** Health, diet and body image, medication and dosing, money and debt, and self-image can affect readers’ choices. Cite [5.1] when the passage substantively provides guidance, claims, or framing likely to affect wellbeing. Cite [5.3] when the passage substantively concerns mental health or self-harm. Do not cite either section for a passing or routine mention. After citing, assess whether the treatment is careful, accurate, and appropriate to the risk.

**Descriptions of people.** The language used to describe people is substantive content. Dehumanising or stigmatising descriptions engage [1.1]. Treating mental illness as entertainment or as an insult engages [5.3], even when the passage does not depict direct harm.

**Sound handling is a finding.** A passage can substantively engage a section and handle it well. State the specific choice that succeeds, then stop. Do not invent a criticism merely to make the assessment appear balanced.

**Contested value questions.** When reasonable people disagree about the relevant values, such as in politically contested issues, identify the disagreement and its competing considerations. Do not take a position unless the passage itself provides a clear reason to do so.
