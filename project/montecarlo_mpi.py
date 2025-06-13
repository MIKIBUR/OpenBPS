from mpi4py import MPI
import numpy as np
import json
import time
from datetime import datetime

class AdvancedMonteCarlo:
    """Advanced Monte Carlo integration with multiple sampling methods"""

    def __init__(self, seed=None):
        if seed is not None:
            np.random.seed(seed)

    def uniform_sampling(self, func, bounds, samples):
        """Standard uniform sampling Monte Carlo"""
        dim = len(bounds)
        points = np.random.uniform(0, 1, (samples, dim))

        # Scale points to actual bounds
        for i, (a, b) in enumerate(bounds):
            points[:, i] = a + (b - a) * points[:, i]

        # Calculate function values
        values = np.array([func(point) for point in points])

        # Calculate volume of integration region
        volume = np.prod([b - a for a, b in bounds])

        return volume * np.mean(values), np.std(values) / np.sqrt(samples)

def test_function_2d(point):
    """2D test function: f(x,y) = sin(\u03c0x) * cos(\u03c0y) * exp(-(x²+y²))"""
    x, y = point
    return np.sin(np.pi * x) * np.cos(np.pi * y) * np.exp(-(x**2 + y**2))

def run_monte_carlo_mpi(samples_total, bounds):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    samples_per_proc = samples_total // size

    mc = AdvancedMonteCarlo(seed=42 + rank)
    start_time = time.time()
    result, error = mc.uniform_sampling(test_function_2d, bounds, samples_per_proc)
    end_time = time.time()

    # Gather results to root
    all_results = comm.gather(result, root=0)
    all_errors = comm.gather(error, root=0)
    all_times = comm.gather(end_time - start_time, root=0)

    if rank == 0:
        avg_result = np.mean(all_results)
        combined_error = np.sqrt(np.sum(np.square(all_errors))) / size
        total_time = max(all_times)

        final_result = {
            'samples_total': samples_total,
            'bounds': str(bounds),
            'result': float(avg_result),
            'error': float(combined_error),
            'computation_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'mpi_ranks': size
        }

        output_file = "/home/pbsuser/project/results/mc_result_mpi.json"
        with open(output_file, 'w') as f:
            json.dump(final_result, f, indent=2)

        print(f"Final MPI result: {avg_result:.6f} ± {combined_error:.6f}")
        print(f"Total computation time: {total_time:.2f} seconds")

if __name__ == "__main__":
    import sys
    import ast

    if len(sys.argv) < 2:
        print("Usage: mpiexec -n <n> python montecarlo_mpi.py <total_samples> [bounds]")
        sys.exit(1)

    samples_total = int(sys.argv[1])

    if len(sys.argv) > 2:
        try:
            bounds = ast.literal_eval(sys.argv[2])
            if not all(isinstance(b, tuple) and len(b) == 2 for b in bounds):
                raise ValueError
        except Exception:
            print("Bounds must be a list of tuples, e.g., \"[(-1,1),(-1,1)]\"")
            sys.exit(1)
    else:
        bounds = [(-1, 1), (-1, 1)]

    run_monte_carlo_mpi(samples_total, bounds)
