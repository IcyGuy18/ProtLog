# protlog/utils/__init__.py

from .colours import colour_text
from .utils import get_transposed_proteins, get_protein_sequence

__all__ = [
    'get_transposed_proteins',
    'get_protein_sequence',
    'colour_text'
]