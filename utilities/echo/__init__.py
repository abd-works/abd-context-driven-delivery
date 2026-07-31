"""Echo - chainable action decorator + Echoer toolset.

Public exports:
    echo     - @echo decorator (marks an @action so its full wrapped instructions are echoed, fenced with DO-NOT-FOLLOW, instead of executed)
    Echoer   - standalone echo toolset (fence tool + echo_session action)

See echo.md for the canonical echo contract.
"""
from echo.echo import Echoer
from echo._decorator import echo  # imported LAST so `from echo import echo` binds to the decorator, not the submodule

__all__ = ["echo", "Echoer"]
