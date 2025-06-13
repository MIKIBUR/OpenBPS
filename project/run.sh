#!/bin/bash

# Check first argument for mode
MODE="$1"

if [[ "$MODE" == "native" ]]; then
  SCRIPT="montecarlo.py"
  shift
elif [[ "$MODE" == "mpi" ]]; then
  SCRIPT="montecarlo_mpi.py"
  shift
else
  # Default mode = native, no shift because first arg is actually samples_per_job
  SCRIPT="montecarlo.py"
fi

# Now $1 and $2 are samples_per_job and bounds, possibly shifted if mode was specified
SAMPLES_PER_JOB="${1:-2000000}"
BOUNDS="${2:-(-1,1),(-1,1)}"


PBS_SCRIPT="/tmp/calc_wrapper_$$.pbs"

cat > "$PBS_SCRIPT" <<EOF
#!/bin/bash
#PBS -N ParallelMonteCarlo
#PBS -J 1-2
#PBS -l walltime=00:05:00
#PBS -l select=1:ncpus=1
#PBS -o /home/pbsuser/project/results/mc_out_\${PBS_ARRAY_INDEX}.txt
#PBS -e /home/pbsuser/project/results/mc_err_\${PBS_ARRAY_INDEX}.txt

SAMPLES_PER_JOB=${SAMPLES_PER_JOB}
BOUNDS='${BOUNDS}'

mkdir -p /home/pbsuser/project/results

echo "========================================="
echo "Parallel Monte Carlo Job \${PBS_ARRAY_INDEX}"
echo "Started at: \$(date)"
echo "Running on: \$(hostname)"
echo "PBS Job ID: \${PBS_JOBID}"
echo "Array Index: \${PBS_ARRAY_INDEX}"
echo "========================================="

cd /home/pbsuser/project

echo "Configuration:"
echo "  Samples per job: \${SAMPLES_PER_JOB}"
echo "  Bounds: \${BOUNDS}"
echo ""

python3 ${SCRIPT} \${PBS_ARRAY_INDEX} \${SAMPLES_PER_JOB} "\${BOUNDS}"

echo ""
echo "Job \${PBS_ARRAY_INDEX} completed at: \$(date)"
echo "========================================="
EOF

qsub "$PBS_SCRIPT"
