import sys, os, datetime
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))

import stories.src.skill.evals.eval as E

E._load_secrets()

orig = E.discover_coarse_cases
E.discover_coarse_cases = lambda: [p for p in orig() if p.name == "04-specification"]

run_dir = E._create_run_dir()
results = E.run_coarse_cases(run_dir=run_dir)
report = E.Report(
    started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    mode="coarse",
    coarse_results=results,
)
E._write_report(report, run_dir)
