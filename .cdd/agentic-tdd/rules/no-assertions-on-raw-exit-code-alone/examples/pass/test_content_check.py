verdict = self.ai_judge(output=result.stdout, rubric="...", ...)
assert verdict.passed(), verdict.reason
