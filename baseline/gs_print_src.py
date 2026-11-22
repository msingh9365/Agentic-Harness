"""Job (CPU kernel, seconds): copy the authors' tokenizer source (pinned commit) to the output, so that the options of their SentencePiece training can be read.   (OURS)"""
import os
import shutil
import sys

from baseline import common as C


def main():
    info = C.setup_nebula(None, require_patched=False)
    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    for rel in ("nebula/preprocessing/tokenization.py", "nebula/constants.py"):
        shutil.copy(os.path.join(info["nebula_root"], rel), os.path.join(out, os.path.basename(rel)))
    print("copied", os.listdir(out))


if __name__ == "__main__":
    main()
