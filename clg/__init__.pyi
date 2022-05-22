import argparse
from typing import Any, Callable, Iterator, NoReturn, Sequence


ACTIONS: dict[str, argparse.Action] = ...
COMPLETERS: dict[str, Callable] = ...


class CLGError(Exception):
    path: list[str]
    msg: str

    def __init__(self, path: list[str], msg: str) -> None:
        ...

    def __str__(self) -> str:
        ...


class NoAbbrevParser(argparse.ArgumentParser):
    ...


class HelpPager(argparse.Action):
    def __init__(self, option_strings: Sequence[str],
                 dest: str, default: str = ...,
                 help: str | None = ...
    ) -> None:
        ...

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: str | Sequence[Any] | None, option_string: str | None = ...
    ) -> None:
        ...


class Namespace(argparse.Namespace):
    def __init__(self, args: dict[str, Any]) -> None:
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def _get(self, key: str, default: Any = ...) -> Any:
        ...

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        ...


class CommandLine(object):
    def __init__(
        self, config: dict[str, Any], keyword: str = ..., deepcopy: bool = ...
    ) -> None:
        ...
    
    def parse(self, args: Sequence[str] | None = ...) -> Namespace:
        ...
    
    def print_help(self, args: Namespace) -> None:
        ...


def init(format: str = ..., data: str = ...,
         completion: bool = ..., subcommands_keyword: str = ..., deepcopy: bool = ...
         ) -> Namespace:
    ...
