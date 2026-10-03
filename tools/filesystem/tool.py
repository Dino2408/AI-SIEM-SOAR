from pathlib import Path
def read_text(path): return Path(path).read_text(encoding="utf-8")
def exists(path): return Path(path).exists()
