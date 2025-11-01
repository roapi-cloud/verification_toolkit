#!/usr/bin/env python3
"""CLI for running batch verification workflows."""

import argparse
import sys
from pathlib import Path

from .config import load_runbook
from .runner import BatchRunner


def main():
    parser = argparse.ArgumentParser(
        description="Run batch verification workflows"
    )
    parser.add_argument(
        "runbook_path",
        help="Path to the runbook YAML file"
    )
    parser.add_argument(
        "--mode",
        choices=["sync", "async", "parallel"],
        default="sync",
        help="Execution mode (default: sync)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum workers for parallel execution (default: 4)"
    )
    parser.add_argument(
        "--output",
        help="Output file for the report (optional)"
    )

    args = parser.parse_args()

    # Load runbook
    try:
        runbook = load_runbook(Path(args.runbook_path))
    except Exception as e:
        print(f"Error loading runbook: {e}", file=sys.stderr)
        sys.exit(1)

    # Create runner
    runner = BatchRunner(runbook, max_workers=args.max_workers)

    # Run batch
    try:
        if args.mode == "sync":
            report = runner.run_batch_sync()
        elif args.mode == "async":
            import asyncio
            report = asyncio.run(runner.run_batch_async())
        else:  # parallel
            report = runner.run_batch_parallel()
    except Exception as e:
        print(f"Error running batch: {e}", file=sys.stderr)
        sys.exit(1)

    # Print report
    report.print_summary()

    # Save report if requested
    if args.output:
        import json
        from dataclasses import asdict

        output_data = asdict(report)
        # Convert dataclasses to dicts
        output_data["results"] = [asdict(r) for r in report.results]

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()