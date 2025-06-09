import numpy as np

def monte_carlo_integrate(f, a, b, samples=1000000):
    x = np.random.uniform(a, b, samples)
    y = f(x)
    return (b - a) * np.mean(y)

if __name__ == "__main__":
    result = monte_carlo_integrate(lambda x: x**2, 0, 1)
    with open("results/result_0.txt", "w") as f:
        f.write(f"Wynik całkowania: {result}\n")
