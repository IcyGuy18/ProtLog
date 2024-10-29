from .aa_calculator import AACalculator, AA
from ..utils import get_transposed_proteins
from numpy import log

class NaturalLogCalculator(AACalculator):

    @staticmethod
    def calculate(sequences: list[str]) -> tuple[int, dict | str]:
        """
        This function calculates the natural log frequency of an
        amino acid against all provided sequences at all positions.

        :param sequences: a list of protein sequences.
        :type sequences: list[str]
        :return: Error code and a table of calculated values.
        :rtype: tuple
        """
        if len(sequences):
            transposed_sequences = get_transposed_proteins(sequences)
            if isinstance(transposed_sequences, str):
                return 2, transposed_sequences
            
            table = dict.fromkeys(transposed_sequences, 0)
            for position, sequence in transposed_sequences.items():
                values_table = dict.fromkeys(AA, 0)
                
                for aa in AA:
                    total = len(sequence)
                    count = sequence.count(aa)
                    values_table[aa] = (
                        log(count / total)
                    )

                table[position] = values_table
            
            return 0, table
        return 1, "Provide at least one protein sequence for computation!"