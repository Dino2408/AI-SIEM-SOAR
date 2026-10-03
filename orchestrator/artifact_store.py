from pathlib import Path

class ArtifactStore:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def _path(self, relative):
        p = (self.root / relative).resolve()
        if self.root not in p.parents and p != self.root:
            raise PermissionError("path escapes repository")
        return p

    def write(self, relative, content, allowed_prefixes):
        if not isinstance(content, str):
            raise TypeError("artifact content must be text")
        if not any(relative == x or relative.startswith(x.rstrip("/") + "/") for x in allowed_prefixes):
            raise PermissionError(f"agent cannot write {relative}")
        if relative == ".git" or relative.startswith(".git/"):
            raise PermissionError("git internals are never writable")
        p = self._path(relative)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p
