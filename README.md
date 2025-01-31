# XSOAR Dependency Graph
[![Python package](https://github.com/tlium/xsoar-dependency-graph/actions/workflows/python-package.yml/badge.svg)](https://github.com/tlium/xsoar-dependency-graph/actions/workflows/python-package.yml)


XSOAR Dependency Graph is a Python utility to create a dependency graph of either an entire content repository
or a single content pack.

## Requirements
In order to create a dependency graph for you content, you need the content to be in [Content Packs Structure](https://xsoar.pan.dev/docs/packs/packs-format).
It is highly recommended to use a content repository similar to [content-ci-cd-template](https://github.com/demisto/content-ci-cd-template) as you probably want
to use [demisto-sdk](https://github.com/demisto/demisto-sdk) to interact with or create content at some point.

## Usage

### Installation

#### PyPI
- `pip install xsoar-dependency-graph`

#### Directly from GitHub
Bleeding edge versions can be installed using pip:
- `pip install git+https://github.com/tlium/xsoar-dependency-graph.git`

### Code examples
Please see [plot_all_packs.py](examples/plot_all_packs.py) or [plot_single_pack.py](examples/plot_single_pack.py) for detailed invocation and code examples.
These two examples uses mock data in the [tests/data/mock_content_repo](tests/data/mock_content_repo) directory, but it should be easy to use your own content repo instead.


## How is the content graph constructed
The content repository path given as a constructor argument is analyzed. For each content pack, the following items are evaluated (in order):
1. The Content Pack itself is added as a graph node
2. Playbooks are added as nodes. Playbooks are parsed and nodes and edges are added for any script or playbook reference found.
3. Layouts are added as nodes. Layouts are parsed and nodes and edges are added when they are found for e.g dynamic sections or buttons.
4. Incident Types are added as nodes. Layouts are parsed and nodes and edges are added for script or playbook references.
5. Integrations are added as nodes. The integrations are parsed and every command defined in the integration is added as graph nodes. Integration code as such is not yet parsed.
6. Scripts are added as nodes. If there is no path between Content Pack (1) and script then an edge is created from Content Pack node to script node. The scripts themselves are parsed as an Abstract Syntax Tree. When calls to `execute_command` or `demisto.executeCommand` are found, the scripts being called are added as graph nodesth an edge back to the calling script.

### I can create a content graph with demisto-sdk, so how does this differ?
I have a slightly different opinion on how the content graph should be constructed. One example is I don't want all content items in a content pack to have an edge back to the
content graph as such. I also want edges between scripts so that I can easily see exactly which other scripts a script is dependent upon and not only a dependency back to the content pack.
Furthermore, demisto-sdk will do all sorts of validation of content which I don't care about. If you have weird docker image definitions in your content that's your business.
I also prefer to plot my graphs with matplotlib initially. Unlike demisto-sdk, I don't care about visualizing the graphs in Neo4j. I would much rather export (this feature is not yet implemented) the finished graph to a format
Neo4j can read, so that people can decide for themselves how they would like the graphs to be used.
