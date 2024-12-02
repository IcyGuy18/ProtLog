"""We're going to define values' calculations here."""
import numpy as np

def get_longest_centered_array(values) -> list[float]:
    left_count, right_count = 0, 0
    for i in range(len(values)): # Count from left
        if values[i] == '-inf':
            left_count += 1
        else:
            break
    
    for i in range(len(values)-1, 0, -1): # Count from right
        if values[i] == '-inf':
            right_count += 1
        else:
            break
    slice_to_make = max(left_count, right_count)
    
    return values[slice_to_make:len(values)-slice_to_make]


def additive_calculator(vector: list[float | int | str]) -> float:
    additive_score = 0.0
    for value in vector:
        if isinstance(value, float | int):
            additive_score += value
    if additive_score == 0.0:
        additive_score = 'NIL'
    return additive_score

def multiplicative_calculator(vector: list[float | str]) -> tuple[bool, dict]:
    # Logic here is that
    # We check if values persist at least as far as 6 positions
    # relative to the modification site.
    # If not, it's NIL.
    # If so, calculate only up to the point it can be allowed.
    vector = get_longest_centered_array(vector)
    if len(vector) < 13:
        return False, {'message': "Not enough upstream/downstream amino acids to make accurate calculation!", 'multiplicative_score': 'NIL', 'adjusted_multiplicative_score': 'NIL'}
    multiplicative_score = 1
    for idx, value in enumerate(vector):
        if (idx != (len(vector) // 2)) and (value == float(0) or value == '-inf'):
            return False, {'message': "Vector contains 0 or negative infinity!", 'multiplicative_score': 'NIL', 'adjusted_multiplicative_score': 'NIL'}
        if (idx != (len(vector) // 2)): # Skip over the center value.
            multiplicative_score *= value
    adjusted_multiplicative_score = np.log(abs(1 / (-1 * multiplicative_score)))
    return True, {'multiplicative_score': multiplicative_score, 'adjusted_multiplicative_score': adjusted_multiplicative_score}
