def test_example(self, tmp_path):
    context = self.given_context("""# My Artifact
This is the artifact text hardcoded as a string in the test body.
""")
    result = self.when_agent_invoked(..., context=context, ...)
    assert "PASS" in result.stdout
