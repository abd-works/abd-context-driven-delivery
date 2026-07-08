_EXAMPLES_DIR = Path(__file__).parent / "examples" / "my-feature"

@pytest.mark.parametrize("example", _collect(), ids=[e.name for e in _collect()])
def test_example(self, example, tmp_path):
    context = (example.context_dir / "artifact.md").read_text()
    ...
