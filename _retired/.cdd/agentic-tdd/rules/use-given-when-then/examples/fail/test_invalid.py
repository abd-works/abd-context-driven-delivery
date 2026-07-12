import subprocess

class TestMyRule:
    def test_example(self):
        result = subprocess.run(["cursor-agent", "-p", "Do something."], capture_output=True)
        assert result.returncode == 0
