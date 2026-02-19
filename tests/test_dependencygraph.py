from pathlib import Path

from xsoar_dependency_graph.xsoar_dependency_graph import ContentGraph


class TestClass:
    def test_initialize_module(self, shared_datadir: Path) -> None:
        repo_path = shared_datadir / "mock_content_repo"
        obj = ContentGraph(repo_path=repo_path)
        obj.create_content_graph(pack_paths=None)
        assert type(obj) is ContentGraph

    def test_create_graph_all_packs(self, shared_datadir: Path) -> None:
        repo_path = shared_datadir / "mock_content_repo"
        obj = ContentGraph(repo_path=repo_path)
        obj.create_content_graph(pack_paths=None)
        assert type(obj) is ContentGraph

    def test_read_global(self, shared_datadir: Path) -> None:
        contents = (shared_datadir / "hello.txt").read_text()
        assert contents == "Hello World!\n"
