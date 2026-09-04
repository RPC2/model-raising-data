"""Export one constitution arm's annotations from compare_cards.json as a review sheet.

Items are ordered worst-judge-score first so a partial read still covers the
most suspect annotations. Writes Markdown with a blank verdict line per item.
"""

import argparse
import json
from pathlib import Path

CARDS_PATH = (
    Path(__file__).resolve().parent.parent / "prompt_pipeline" / "compare_cards.json"
)


def _fmt_scores(scores: dict) -> str:
    """Render the judge's per-dimension scores on one line."""
    return "  ".join(f"{k}={v}" for k, v in scores.items())


def _render(item: dict, arm_name: str, rank: int, total: int) -> str:
    """Render one item as a Markdown review block."""
    arm = item["arms"][arm_name]
    point = int(item["reflection_point"])
    text = item["text"]
    seen, unseen = text[:point], text[point:]
    lines = [
        f"## {rank}/{total} — `{item['item_id']}`",
        "",
        f"- safety_score **{item['safety_score']}** | reflection_point {point}",
        f"- judge: **{arm['judge_decision']}** agg **{arm['judge_aggregate']}** | {_fmt_scores(arm['judge_scores'])}",
        f"- charter_elements: `{arm['charter_elements']}`",
        "",
        "### Document the model SAW",
        "",
        "```",
        seen.strip() or "(empty)",
        "```",
        "",
        "### Continues (model did NOT see)",
        "",
        "```",
        (unseen.strip()[:400] + ("..." if len(unseen.strip()) > 400 else ""))
        or "(nothing)",
        "```",
        "",
        "### reflection_1p",
        "",
        arm["reflection_1p"].strip() or "**(EMPTY)**",
        "",
        "### reflection_3p",
        "",
        arm["reflection_3p"].strip() or "**(EMPTY)**",
        "",
        "<details><summary>judge reasoning</summary>",
        "",
        arm["judge_reasoning"].strip(),
        "",
        "</details>",
        "",
        "**YOUR VERDICT:** ",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Write the review sheet for one arm, worst judge score first."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", default="MR v0.2")
    parser.add_argument("--limit", type=int, default=0, help="0 = all items")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))
    run = next(r for r in cards["runs"] if r["label"] == args.arm)
    items = sorted(
        cards["items"], key=lambda i: float(i["arms"][args.arm]["judge_aggregate"])
    )
    if args.limit:
        items = items[: args.limit]

    header = [
        f"# Review sheet — {args.arm}",
        "",
        f"- run `{run['run_id']}` | generator **{run['gen_model']}** / `{run['prompt']}`",
        f"- constitution `{run['constitution']}` | guidelines `{run['guidelines']}`",
        f"- judge **{run['judge_model']}** / `{run['judge_prompt']}`",
        f"- {len(items)} items, worst judge score first",
        "",
        "Fill in **YOUR VERDICT** under each item. Suggested shorthand:",
        "`ok` · `generic` (could apply to any doc) · `overcited` (citation not supported)",
        "· `preachy` · `samevoice` (3p is just 1p passivised) · `wrong` (misreads the doc)",
        "",
        "---",
        "",
    ]
    body = [_render(it, args.arm, n, len(items)) for n, it in enumerate(items, 1)]
    args.out.write_text("\n".join(header) + "".join(body), encoding="utf-8")
    print(f"wrote {args.out} ({len(items)} items)")


if __name__ == "__main__":
    main()
