from verification_toolkit import GitHubIssuePreparer, EvaluationResult, VerificationAgent
from verification_toolkit.batch_workflow import load_runbook, BatchRunner

# 1. 自定义 Agent
class MyAgent(VerificationAgent):
    def run_verification(self, context):
        details = f"Repo: {context.owner}/{context.project}\nIssue: {context.issue_number}\nCommit: {context.current_commit}\n"
        return EvaluationResult(success=True, details=details, artifacts={"repo_path": context.repo_path})

# 2. 单个 Issue 验证流程
def single_issue_demo(issue_url):
    preparer = GitHubIssuePreparer()
    context = preparer.prepare(issue_url)
    agent = MyAgent()
    result = agent.run_verification(context)
    print("Single Issue Verification Result:")
    print("Success:", result.success)
    print("Details:", result.details)
    print("Artifacts:", result.artifacts)

# 3. 批量工作流流程
def batch_demo(runbook_path):
    runbook = load_runbook(runbook_path)
    runner = BatchRunner(runbook)
    report = runner.run_batch_sync()
    print("\nBatch Workflow Summary:")
    report.print_summary()

if __name__ == "__main__":
    # 单个 issue 验证
    single_issue_demo("https://github.com/microsoft/vscode/issues/1")
    # 批量工作流（需准备好 demo_runbook.yaml）
    batch_demo("demo_runbook.yaml")
