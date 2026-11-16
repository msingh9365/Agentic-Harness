"""Build a small flat sample of the Speakeasy reports (symlinks) for local tests: N files per class and split.
The Hugging Face copy shards some folders into sub-folders; the Kaggle copy is flat (what the pipeline expects)."""
import os
import sys


def make_sample(src, dest, per_class=20):
    os.makedirs(dest, exist_ok=True)
    for split in ["trainset", "testset"]:
        sdir = os.path.join(src, f"windows_emulation_{split}")
        for folder in sorted(x for x in os.listdir(sdir) if x.startswith("report_")):
            out = os.path.join(dest, f"windows_emulation_{split}", folder)
            os.makedirs(out, exist_ok=True)
            files = []
            for dp, _, fn in os.walk(os.path.join(sdir, folder)):
                files += [os.path.join(dp, f) for f in fn if f.endswith(".json")]
            for f in sorted(files)[:per_class]:
                dst = os.path.join(out, os.path.basename(f))
                if not os.path.exists(dst):
                    os.symlink(os.path.abspath(f), dst)
    return dest


if __name__ == "__main__":
    print(make_sample(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20))
