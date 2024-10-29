import abc

AA = "A C D E F G H I K L M N P Q R S T V W Y".split(' ')

class AACalculator(abc.ABC):
    
    @staticmethod
    def calculate() -> None:
        """
        Template method.
        
        This is designed to inherit and make your own calculations from.
        """
        ...