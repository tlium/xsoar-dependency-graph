import ast
from typing import Any


class FunctionCallFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls = []
        self.script_names = []

    def _get_executed_command(self, node: ast.Call) -> str:
        executed: str = ""
        if node.args:
            if isinstance(node.args[0], ast.Constant):
                executed = node.args[0].value  # ty: ignore[invalid-assignment]
            elif isinstance(node.args[0], ast.JoinedStr):
                # We probably have something like an f-string argument to the function here
                # Ignore for now. Parsing to be implemented
                executed = ""
            elif isinstance(node.args[0], ast.Attribute):
                # Not yet implemented
                executed = ""
            else:
                executed = ""
        elif node.keywords:
            kw = {kw.arg: kw.value for kw in node.keywords}
            if isinstance(kw["command"], ast.Constant):
                executed = str(kw["command"].value)
            elif isinstance(kw["command"], ast.Name):
                # Not yet implemented
                executed = ""
            else:
                # Not yet implemented
                executed = ""
        if executed == "executeCommandAt":
            if node.args:
                executed = node.args[0].value  # ty: ignore[unresolved-attribute]
                if isinstance(executed, ast.Name):
                    # Not yet implemented
                    executed = ""
            elif node.keywords:
                d = {kw.arg: kw.value for kw in node.keywords}
                d2 = {k.value: v for k, v in zip(d["args"].keys, d["args"].values, strict=False)}  # ty: ignore[unresolved-attribute]
                executed = d2["command"].value
        if isinstance(executed, ast.Name):
            print(ast.dump(node))
        return executed

    def visit_Call(self, node: ast.Call) -> Any:  # noqa: ANN401, N802
        executed = ""

        if isinstance(node.func, ast.Name) and node.func.id == "execute_command":
            executed = self._get_executed_command(node)

        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "demisto" and node.func.attr == "executeCommand":
                executed = self._get_executed_command(node)

        if executed:
            self.script_names.append(executed)

        return self.generic_visit(node)
