import ast
from pathlib import Path

from xsoar_dependency_graph.utils.ast_utils import FunctionCallFinder

from .basic_parser import BasicParser


class ScriptParser(BasicParser):
    def __init__(self, script_path: Path) -> None:
        super().__init__()
        self.data = super().load_yaml(script_path)
        self.script_path = script_path
        # print(f"  - parsing {script_path}")

    def get_script_id(self) -> str:
        return self.data["commonfields"]["id"]

    def parse(self) -> list[tuple]:
        """Adds a graph node for the script itself. Also parses the script with AST and finds
        any reference to execute_command or demisto.executeCommand and creates script nodes for
        whatever commands are executed in the script."""

        script_id = self.get_script_id()

        # This is where we would want to parse the Python files with AST
        if self.data["type"] != "python":
            return []
        if self.data["script"] and self.data["script"] != "-":
            # We have an inline script. Try to fetch it
            script_data = self.data["script"]
        else:
            python_path = Path(self.script_path.with_name(self.script_path.stem + ".py"))
            script_data = python_path.open("r").read()

        try:
            # Make an Abstract Syntax Tree of the Python source code and extract calls to `demisto.executeCommand` and
            # `execute_command`
            tree = ast.parse(script_data)
            visitor = FunctionCallFinder()
            visitor.visit(tree)
            edges = [(script_id, item) for item in visitor.script_names]

        except SyntaxError:
            # You may want to check the source code that is being parsed here . One of the
            # most common causes for this exception to occur is when you have a `lambda`
            # definition with parentheses around its arguments. This was allowed in Python 2
            # but not in Python3. Of course you may have a simple Syntax Error as well, but either
            # way we ignore this errro and continue. The only down side is the script will not be
            # parsed properly and the graph may be missing a few nodes.
            return []
        except Exception as ex:
            raise RuntimeError from ex

        return edges
