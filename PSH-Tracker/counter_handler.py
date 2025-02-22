
def IncrementCount(current_value, increment_amount):
    return current_value + increment_amount

def DecrementCount(current_value, increment_amount):
    return max(0, current_value - increment_amount)  # Prevent going below 0