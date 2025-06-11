import numpy as np
import sys
import json
import time
from datetime import datetime
import ast

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
    """2D test function: f(x,y) = sin(πx) * cos(πy) * exp(-(x²+y²))"""
    x, y = point
    return np.sin(np.pi * x) * np.cos(np.pi * y) * np.exp(-(x**2 + y**2))

def run_monte_carlo_job(job_id, samples_per_job, bounds, method='uniform'):
    """Run a single Monte Carlo job"""
    
    # Initialize Monte Carlo with unique seed per job
    mc = AdvancedMonteCarlo(seed=42 + job_id)
    
    start_time = time.time()
    
    # Run calculation based on method

    result, error = mc.uniform_sampling(test_function_2d, bounds, samples_per_job)
    
    end_time = time.time()
    
    # Prepare results
    job_result = {
        'job_id': job_id,
        'samples': samples_per_job,
        'bounds' : str(bounds),
        'result': float(result),
        'error': float(error),
        'computation_time': end_time - start_time,
        'timestamp': datetime.now().isoformat()
    }
    
    return job_result

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 montecarlo_advanced.py <job_id> [samples] [bounds]")
        sys.exit(1)
    
    job_id = int(sys.argv[1])
    samples_per_job = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    
    if len(sys.argv) > 3:
        try:
            bounds = ast.literal_eval(sys.argv[3])
            if not all(isinstance(b, tuple) and len(b) == 2 for b in bounds):
                raise ValueError
        except Exception:
            print("Bounds must be a list of tuples, e.g., \"[(-1,1),(-1,1)]\"")
            sys.exit(1)
    else:
        bounds = [(-1, 1), (-1, 1)]
    
    print(f"Starting Monte Carlo job {job_id}")
    print(f"Samples: {samples_per_job}")
    print(f"Bounds: {bounds}")
    
    try:
        # Run the calculation
        result = run_monte_carlo_job(job_id, samples_per_job, bounds)
        
        # Save individual result
        output_file = f"/home/pbsuser/project/results/mc_result_{job_id}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Job {job_id} completed successfully")
        print(f"Result: {result['result']:.6f} ± {result['error']:.6f}")
        print(f"Time: {result['computation_time']:.2f} seconds")
        
    except Exception as e:
        print(f"Error in job {job_id}: {str(e)}")
        # Save error info
        error_result = {
            'job_id': job_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        output_error_file = f"/home/pbsuser/project/results/mc_error_{job_id}.json"
        with open(output_error_file, 'w') as f:
            json.dump(error_result, f, indent=2)
        sys.exit(1)