"""conf_secrets fills missing env keys from dotenv-style files."""
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import context, description, it

from utilities.conf_secrets import load_conf_secrets, parse_dotenv


with description("conf_secrets"):
    with context("given dotenv-style lines"):
        with it("should parse keys and skip comments"):
            parsed = parse_dotenv("# c\nOPENAI_API_KEY=sk-test\n\nPINECONE_INDEX=abd-answers\n")
            expect(parsed.get("OPENAI_API_KEY")).to(equal("sk-test"))
            expect(parsed.get("PINECONE_INDEX")).to(equal("abd-answers"))

    with context("given a kit conf/.secrets that imports another file"):
        with it("should fill missing keys and leave existing env alone"):
            kit = Path(os.environ.get("TEMP") or "/tmp") / "cdd-conf-secrets-spec"
            answers = kit / "answers.secrets"
            conf = kit / "conf"
            conf.mkdir(parents=True, exist_ok=True)
            answers.write_text(
                "OPENAI_API_KEY=from-answers\nPINECONE_API_KEY=pcsk-test\n",
                encoding="utf-8",
            )
            (conf / ".secrets").write_text(
                f"CONTENT_MEMORY_ROOT=C:/memory\nSECRETS_IMPORT={answers}\n",
                encoding="utf-8",
            )
            env = {"OPENAI_API_KEY": "already-set"}
            loaded = load_conf_secrets(kit, environ=env)
            expect(env.get("OPENAI_API_KEY")).to(equal("already-set"))
            expect(env.get("PINECONE_API_KEY")).to(equal("pcsk-test"))
            expect(env.get("CONTENT_MEMORY_ROOT")).to(equal("C:/memory"))
            expect("SECRETS_IMPORT" in env).to(equal(False))
            expect(len(loaded) >= 1).to(equal(True))
