"""
A placeholder class that can be used for debugging purposes.
Meant as a library of sorts.
"""

from .utils import colour_text

class Protein:
    def __init__(self, accession: str, sequence: str) -> None:
        self.__accession = accession
        self.__sequence = sequence
    
    def __repr__(self) -> str:
        return (
            "Protein("
                f"accession='{self.accession}',"
                f"sequence='{self.sequence}'"
            ")"
        )
    
    @property
    def sequence(self) -> str:
        return self.__sequence
    
    @property
    def accession(self) -> str:
        return self.__accession
    
    def get_sequence(self, num_seqs_on_line: int = 5) -> str:
        """
        Display the amino acid sequence of the protein in a readable format.

        :param num_seqs_on_line: how many chunks of sequences should appear
            in a line before going to the next line, defaults to 5
        :type num_seqs_on_line: int
        """

        # Yeah it's pretty shoddy.
        # Best to not touch it.
        # Least it works as intended!

        rep = ''
        splits = [
            self.sequence[i:i + 10] for i in range(0, len(self.sequence), 10)
        ]
        rep += (
            colour_text(
                f'Accession: {self.accession}', colour='red', style='bold'
            ) + "\n\n"
        )
        total = 0
        subsequences = []
        rep += ' ' * (8 - len(str(total)))
        for i in range(len(splits)):
            if i % num_seqs_on_line == 0 and i != 0:
                rep += '\n' + '\t'.join(subsequences)
                rep += "\n\n" + (' ' * (8 - len(str(total))))
                subsequences = []
            rep += (
                "["
                + colour_text(total, colour='blue', style='both')
                + "]\t"
                + (' ' * (8 - len(str(total))) )
            )
            total += len(splits[i])
            subsequences.append(splits[i])
            if len(splits[i]) < 10:
                subsequences[-1] += '.' * (10 - len(splits[i]))
        rep += '\n' + '\t'.join(subsequences)
        return rep