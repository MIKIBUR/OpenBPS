#!/usr/bin/env python3
import json
import glob
import numpy as np
import sys
from collections import defaultdict
from datetime import datetime

def load_results(results_dir="results"):
    """Load all Monte Carlo results from JSON files"""
    results = []
    error_files = []
    
    # Load successful results
    result_files = glob.glob(f"{results_dir}/mc_result_*.json")
    for file_path in sorted(result_files):
        try:
            with open(file_path, 'r') as f:
                result = json.load(f)
                results.append(result)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    # Check for error files
    error_files = glob.glob(f"{results_dir}/mc_error_*.json")
    if error_files:
        print(f"Found {len(error_files)} error files:")
        for error_file in error_files:
            try:
                with open(error_file, 'r') as f:
                    error_data = json.load(f)
                    print(f"  Job {error_data['job_id']}: {error_data['error']}")
            except:
                print(f"  Could not read {error_file}")
    
    return results, error_files

def analyze_results(results):
    """Analyze and summarize Monte Carlo results from identical configurations"""
    if not results:
        print("No results to analyze!")
        return

    print("=" * 60)
    print("MONTE CARLO RESULTS SUMMARY")
    print("=" * 60)

    values = [r['result'] for r in results]
    errors = [r['error'] for r in results]
    times = [r['computation_time'] for r in results]
    total_samples = sum(r['samples'] for r in results)

    # Summary statistics
    mean_result = np.mean(values)
    std_result = np.std(values)
    sem_result = std_result / np.sqrt(len(values))  # Standard error of the mean
    mean_error = np.mean(errors)
    total_time = sum(times)
    mean_time = np.mean(times)

    print(f"  Number of jobs: {len(results)}")
    print(f"  Total samples: {total_samples:,}")
    print(f"  Mean result: {mean_result:.6f} ± {sem_result:.6f}")
    print(f"  Standard deviation: {std_result:.6f}")
    print(f"  Mean Monte Carlo error: {mean_error:.6f}")
    print(f"  Total computation time: {total_time:.2f} seconds")
    print(f"  Mean time per job: {mean_time:.2f} seconds")
    print(f"  Efficiency: {total_samples / total_time:.0f} samples/second")

    return {
        'jobs': len(results),
        'samples': total_samples,
        'mean_result': mean_result,
        'std_error': sem_result,
        'total_time': total_time,
        'efficiency': total_samples / total_time
    }

def create_comparison_plot(summary_data, output_file="results/monte_carlo_comparison.png"):
    """Create comparison plots of different methods"""

    import matplotlib.pyplot as plt

    if not summary_data:
        return
    
    # Group by function
    functions = list(set(d['function'] for d in summary_data))
    methods = list(set(d['method'] for d in summary_data))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Monte Carlo Methods Comparison', fontsize=16)
    
    # Plot 1: Results comparison
    ax1 = axes[0, 0]
    for func in functions:
        func_data = [d for d in summary_data if d['function'] == func]
        if func_data:
            methods_list = [d['method'] for d in func_data]
            results = [d['mean_result'] for d in func_data]
            errors = [d['std_error'] for d in func_data]
            
            x_pos = np.arange(len(methods_list))
            ax1.errorbar(x_pos, results, yerr=errors, marker='o', label=f'{func.upper()} function')
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(methods_list)
    
    ax1.set_title('Integration Results by Method')
    ax1.set_ylabel('Result Value')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Efficiency comparison
    ax2 = axes[0, 1]
    for func in functions:
        func_data = [d for d in summary_data if d['function'] == func]
        if func_data:
            methods_list = [d['method'] for d in func_data]
            efficiency = [d['efficiency'] for d in func_data]
            
            x_pos = np.arange(len(methods_list))
            ax2.bar(x_pos + 0.1*functions.index(func), efficiency, 
                   width=0.3, label=f'{func.upper()} function', alpha=0.7)
    
    ax2.set_title('Computational Efficiency')
    ax2.set_ylabel('Samples/Second')
    ax2.set_xticks(np.arange(len(methods)))
    ax2.set_xticklabels(methods)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Time comparison
    ax3 = axes[1, 0]
    method_times = defaultdict(list)
    for d in summary_data:
        method_times[d['method']].append(d['total_time'])
    
    methods_list = list(method_times.keys())
    times_list = [np.mean(method_times[method]) for method in methods_list]
    
    ax3.bar(methods_list, times_list, alpha=0.7, color=['blue', 'orange', 'green'][:len(methods_list)])
    ax3.set_title('Average Total Time by Method')
    ax3.set_ylabel('Time (seconds)')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Number of jobs
    ax4 = axes[1, 1]
    method_jobs = defaultdict(int)
    for d in summary_data:
        method_jobs[d['method']] += d['jobs']
    
    methods_list = list(method_jobs.keys())
    jobs_list = [method_jobs[method] for method in methods_list]
    
    ax4.bar(methods_list, jobs_list, alpha=0.7, color=['red', 'purple', 'brown'][:len(methods_list)])
    ax4.set_title('Number of Jobs by Method')
    ax4.set_ylabel('Number of Jobs')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nComparison plot saved to: {output_file}")
    
    return fig

def save_summary_report(summary_data, results, output_file="/home/pbsuser/project/results/monte_carlo_report.txt"):
    """Save detailed summary report"""
    with open(output_file, 'w') as f:
        f.write("PARALLEL MONTE CARLO INTEGRATION REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Total jobs analyzed: {len(results)}\n")
        f.write(f"Total samples processed: {sum(r['samples'] for r in results):,}\n")
        f.write(f"Total computation time: {sum(r['computation_time'] for r in results):.2f} seconds\n\n")

        f.write("SUMMARY:\n")
        f.write(f"  Jobs: {summary_data['jobs']}\n")
        f.write(f"  Samples: {summary_data['samples']:,}\n")
        f.write(f"  Result: {summary_data['mean_result']:.6f} ± {summary_data['std_error']:.6f}\n")
        f.write(f"  Time: {summary_data['total_time']:.2f}s\n")
        f.write(f"  Efficiency: {summary_data['efficiency']:.0f} samples/s\n\n")
    
    print(f"Detailed report saved to: {output_file}")

if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "/home/pbsuser/project/results"
    
    print("Loading Monte Carlo results...")
    results, error_files = load_results(results_dir)
    
    if not results:
        print("No results found!")
        sys.exit(1)
    
    print(f"Loaded {len(results)} successful results")
    
    # Analyze results
    summary_data = analyze_results(results)
    mpl_works = True
    # Create plots (requires matplotlib)
    try:
        create_comparison_plot(summary_data)
    except ImportError:
        print("Matplotlib not available - skipping plots")
        mpl_works = False
    except Exception as e:
        print(f"Error creating plots: {e}")
    
    # Save detailed report
    save_summary_report(summary_data, results)
    
    print("\n" + "="*60)
    print("Analysis complete! Check the results directory for:")
    print("  - Individual job results: mc_result_*.json")
    if(mpl_works):
        print("  - Comparison plot: monte_carlo_comparison.png")
    print("  - Summary report: monte_carlo_report.txt")
    print("="*60)