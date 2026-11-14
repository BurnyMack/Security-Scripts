"""LogParse package.

Exports are resolved lazily so that importing the package (or the parser
submodule) does not drag in pandas — only ``LogAnalyzer`` needs it, and only
the xlsx output path uses pandas.
"""

__all__ = ["LogParse", "LogAnalyzer"]


def __getattr__(name):
    if name == "LogParse":
        from .LogParse import LogParse

        return LogParse
    if name == "LogAnalyzer":
        from .LogAnalyse import LogAnalyzer

        return LogAnalyzer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
