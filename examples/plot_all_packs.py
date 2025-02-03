from pathlib import Path

# Import the ContentGraph class from the dependency_graph module
from xsoar_dependency_graph import ContentGraph

# This uses the mock content repository in <project_directory>/tests/data
# If you have a content repository please use:
#   repo_path = Path("/your/package/repo/path")  # noqa: ERA001
repo_path = Path(__file__).parent.resolve().parent.resolve()
repo_path = Path(repo_path / "tests/data/mock_content_repo")
upstream_path = Path("/Users/torben/Source/DNB/XSOAR/upstream-content")

# Instantiate a ContentGraph object using debug mode.
cg = ContentGraph(repo_path=repo_path, upstream_repo_path=upstream_path)

# Create the content graph
# cg.create_content_graph()
cg.add_nodes_from_upstream()

# Plot the content graph
cg.plot_connected_components()
