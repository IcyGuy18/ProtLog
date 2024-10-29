"""
This file contains utility function(s) for performing
various tasks not designated within object-oriented
methodologies.

In other words, their incorporation into classes
made no sense.
""" # As does probably everything else too, but it's more organised this way.

import requests
from typing import Literal


def get_transposed_proteins(sequences: list[str]) -> dict | str:
    """
    Used internally. This function transposes the sequences
    to be used in calculation of values for the table.

    :param sequences: A list of protein sequences.
    :type sequences: list[str]
    :return: A dictionary containing amino acids at individual positions,
        or error code.
    :rtype: dict, str
    """
    # Divide by 2 to get the idea
    if sequences[0] % 2 == 1:
        sequence_length = len(sequences[0]) // 2

        transposed = list(map(''.join, zip(*sequences)))
        pos = [
            '+' + str(i) if i > 0 else str(i)
            for i in range(-1 * sequence_length, sequence_length + 1)
        ]
        return {i: seq for i, seq in zip(pos, transposed)}
    return "Cannot create transpose for even-length sequences - must be odd!"

def get_protein_sequence(
    id: str,
    get_from: Literal['ebi', 'uniprotkb', 'uniparc']
) -> tuple[int, str]:
    """
    Fetch a protein sequence based on the provided ID.

    :param id: The ID to be used for fetching the protein sequence.

        Make sure that, for 'ebi' and 'uniprotkb', the ID has to be
        an accession number.
        
        For 'uniparc', the ID has to be a UniParc Identifier.
    :type id: str

    :param get_from: Where to fetch the protein sequence from.
    :type get_from: str

    :return: A tuple of error code and the protein sequence, or error
        message if error code is not zero.
    :rtype: tuple
    """

    URLS = {
        'ebi': ['http://www.ebi.ac.uk/proteins/api/proteins/{id}',
               'sequence'],
        'uniprotkb': ['https://rest.uniprot.org/uniprotkb/{id}',
                     'value'],
        'uniparc': ['https://rest.uniprot.org/uniparc/{id}',
                   'value'],
    }

    error_code = 0
    # Get the response.
    try:
        response = requests.get(
            f'http://www.ebi.ac.uk/proteins/api/proteins/{URLS[get_from][0]}'
        )
    except Exception as e:
        error_code = 1
        sequence = "Connection error: " + str(e)
    # Extract the sequence.
    try:
        sequence = response.json()['sequence'][URLS[get_from][1]]
    except Exception as e:
        error_code = 2
        sequence = "No sequence found for " + id + ": " + str(e)
    return error_code, sequence

def construct_subsequence(protein: str, site: int, no_stream_aa: int = 10) -> str:
    """
    Construct a subsequence from the protein sequence for PTM dataset.
    
    :param protein: The protein sequence to extract the subsequence from.
    :type protein: str

    :param site: The amino acid where PTM is taking place.
    :type get_from: int

    :param no_stream_aa: How many upstream and downstream amino acids should
        be retrieved alongside the modification site.

        The default is set to 10 for accounting subsequence length in dbPTM.
    :type no_stream_aa: int

    :return: The extracted subsequence.
    :rtype: str
    """
    # Treat PTM site as 0-based (so subtract 1 for convenience)
    start = max(0, site - no_stream_aa)
    end = min(len(protein), site + no_stream_aa + 1)

    subsequence: str = protein[start:end]

    if site < no_stream_aa:
        subsequence = ('-' * (no_stream_aa - site)) + subsequence 
    if site + no_stream_aa > len(protein):
        subsequence += ('-' * ((site + no_stream_aa + 1) - len(protein)))
    
    return subsequence
