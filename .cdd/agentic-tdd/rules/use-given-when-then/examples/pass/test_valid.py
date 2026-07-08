from agentic_tdd import AgentTest

class TestMyRule(AgentTest):
    def test_example(self, tmp_path):
        guidance = self.given_guidance()
        context = self.given_context("some artifact")
        result = self.when_agent_invoked(
            guidance=guidance,
            prompt="Validate this and emit PASS or FAIL.",
            context=context,
            workspace=tmp_path,
            session_file=SESSION_DIR / "my-rule.json",
        )
        verdict = self.ai_judge(
            output=result.stdout,
            rubric="Output must contain PASS.",
            workspace=tmp_path,
            session_file=SESSION_DIR / "my-rule-judge.json",
        )
        assert verdict.passed(), verdict.reason
