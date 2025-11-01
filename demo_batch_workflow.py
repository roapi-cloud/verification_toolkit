#!/usr/bin/env python3
"""Demo script showing how to use the batch workflow from verification_toolkit."""

from verification_toolkit.batch_workflow import BatchRunner, load_runbook

def main():
    """Run a demo batch workflow."""
    # Load runbook
    runbook = load_runbook("demo_runbook.yaml")

    print(f"Loaded runbook: {runbook.name}")
    print(f"Number of jobs: {len(runbook.jobs)}")
    print(f"Max parallel: {runbook.max_parallel}")

    # Create runner
    runner = BatchRunner(runbook)

    # Run batch (synchronously for demo)
    print("\nRunning batch workflow...")
    report = runner.run_batch_sync()

    # Print results
    report.print_summary()

if __name__ == "__main__":
    main()