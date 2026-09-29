"""Run the charter.scale preflections generator on the mini sidecar against OpenRouter.

Same SidecarReader -> AnnotationGenerator path and config as the local sglang run;
only the endpoint (SGLANG_ENDPOINT / SGLANG_API_KEY env) and model name differ.
"""

import sys

from pipeline.charter.scale.generate import AnnotationGenerator
from pipeline.charter.scale.reader import SidecarReader
from pipeline.config import load_config

OPENROUTER_MODEL = "qwen/qwen3.5-35b-a3b"


def main():
    """Process rank 0 (all rows) in-process."""
    cfg = load_config(sys.argv[1:])
    sc = cfg.charter.scale
    reader = SidecarReader(sidecar_path=sc.sidecar_path, rows_per_task=sc.rows_per_task)
    generator = AnnotationGenerator(
        run_name="preflections",
        generator_alias=sc.generator_alias,
        model_name=OPENROUTER_MODEL,
        prompt_filename=sc.preflection_prompt,
        output_dir=sc.output_dir,
        max_concurrent_requests=sc.max_concurrent_requests,
        save_batch_size=sc.save_batch_size,
        thinking=sc.thinking,
        json_mode=sc.json_mode,
        include_reflection_3p=sc.include_reflection_3p,
        canary_seed=sc.canary_seed,
        reflection_seed=sc.reflection_seed,
        disable_canaries=sc.disable_canaries,
        max_retries_per_doc=sc.max_retries_per_doc,
        progress_interval=sc.progress_interval,
        max_text_tokens=cfg.max_tokens,
    )
    list(generator.run(reader.run(rank=0), rank=0))


if __name__ == "__main__":
    main()
