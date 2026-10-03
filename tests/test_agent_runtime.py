from orchestrator.artifact_store import ArtifactStore

def test_artifact_store_blocks_escape(tmp_path):
    store = ArtifactStore(tmp_path)
    try:
        store.write("../escape.txt", "x", ("src",))
    except PermissionError:
        pass
    else:
        raise AssertionError("path escape was not blocked")

def test_artifact_store_allows_declared_prefix(tmp_path):
    store = ArtifactStore(tmp_path)
    p = store.write("src/example.py", "print('ok')", ("src",))
    assert p.read_text(encoding="utf-8") == "print('ok')"
