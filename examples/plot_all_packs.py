from pathlib import Path

# Import the ContentGraph class from the dependency_graph module
from xsoar_dependency_graph import ContentGraph

# This uses the mock content repository in <project_directory>/tests/data
# If you have a content repository please use:
#   repo_path = Path("/your/package/repo/path")  # noqa: ERA001
repo_path = Path(__file__).parent.resolve().parent.resolve()
repo_path = Path(repo_path / "tests/data/mock_content_repo")

# Instantiate a ContentGraph object using debug mode.
cg = ContentGraph(repo_path=repo_path)

# Create the content graph
exclude_list = ["Lium_dev"]
cg.create_content_graph(pack_name="", exclude_list=exclude_list)

# Plot the content graph
cg.plot_graph()
