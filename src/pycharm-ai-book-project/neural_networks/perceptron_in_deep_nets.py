# A perceptron in its simplest form
def perceptron(inputs, weights, bias):
    total = sum(i * w for i, w in zip(inputs, weights)) + bias

    return 1 if total > 0 else 0


# Example: loan approval
income, credit_score, debt_ratio = 50000, 720, 0.3
weights = [0.0001, 0.01, -5]     # Learned from data
bias = -3
approved = perceptron([income, credit_score, debt_ratio], weights, bias)

print(approved)  # Output: 1 (approved)