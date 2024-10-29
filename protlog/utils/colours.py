# Here's some colour codes I use for pretty printing essentially.
import os
from typing import Literal

COLOURS = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "MAGENTA": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

STYLES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "italic": "\033[3m",
    "both": "\033[1m\033[3m",
}

def colour_text(
    *args,
    colour: Literal[
        "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    ],
    style: Literal[
        "reset",
        "bold", "italic", "both"
    ] = "reset"
) -> str:
    text = ' '.join(str(i) for i in args)
    return STYLES[style] + COLOURS[colour] + text + COLOURS['reset']