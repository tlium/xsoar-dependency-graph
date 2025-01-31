from pathlib import Path

import xsoar_dependency_graph

class TestClass:
    def test_initialize_module(self, shared_datadir: Path) -> None:
        repo_path = shared_datadir / "mock_content_repo"
        obj = xsoar_dependency_graph.ContentGraph(repo_path=repo_path)
        obj.create_content_graph()
        assert type(obj) is xsoar_dependency_graph.ContentGraph

    def test_create_graph_all_packs(self, shared_datadir: Path) -> None:
        repo_path = shared_datadir / "mock_content_repo"
        obj = xsoar_dependency_graph.ContentGraph(repo_path=repo_path)
        obj.create_content_graph()
        assert type(obj) is xsoar_dependency_graph.ContentGraph

    def test_read_global(self, shared_datadir: Path) -> None:
        contents = (shared_datadir / "hello.txt").read_text()
        assert contents == "Hello World!\n"
