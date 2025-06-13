#!/bin/bash

# Check first argument for mode
MODE="$1"

if [[ "$MODE" == "native" ]]; then
    SCRIPT="montecarlo.py"
    IS_MPI=false
    shift
elif [[ "$MODE" == "mpi" ]]; then
    SCRIPT="montecarlo_mpi.py"
    IS_MPI=true
    shift
else
    # Default mode = native, no shift because first arg is samples_per_job
    SCRIPT="montecarlo.py"
    IS_MPI=false
fi

# Now $1 and $2 are samples_per_job and bounds
SAMPLES_PER_JOB="${1:-2000000}"
BOUNDS="${2:-(-1,1),(-1,1)}"

###
# IF YOU WANT TO MODIFY AMOUNT OF 'NODES' CHANGE THE -n 2 FLAG BELOW
###
if [[ "$IS_MPI" == true ]]; then
    su - pbsuser -c "mpiexec -n 2 python3 /home/pbsuser/project/montecarlo_mpi.py ${SAMPLES_PER_JOB} \"${BOUNDS}\""
else
# Create a temporary PBS script
PBS_SCRIPT="/tmp/calc_wrapper_$$.pbs"
###
# IF YOU WANT TO MODIFY AMOUNT OF 'NODES' CHANGE THE #PBS -J 1-2 LINE BELOW
###
cat > "$PBS_SCRIPT" <<EOF
#!/bin/bash
#PBS -N ParallelMonteCarlo
#PBS -J 1-2
#PBS -l walltime=00:05:00
#PBS -l select=1:ncpus=1
#PBS -e /home/pbsuser/project/results/mc_err.txt

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

# Run the appropriate Python script
EOF



# Finish script
cat >> "$PBS_SCRIPT" <<EOF

echo ""
echo "Job \${PBS_ARRAY_INDEX} completed at: \$(date)"
echo "========================================="
EOF
echo ""
echo "Jobs submitted succesfully!"
echo "Output files: /home/pbsuser/project/results/mc_result_$.json"
echo "Error log: /home/pbsuser/project/results/mc_err.txt"
echo "For complete results run aggregation script: 'python3 /home/pbsuser/project/aggregate_results.py'"
echo ""
# Submit the job as pbsuser
su - pbsuser -c "qsub '$PBS_SCRIPT'"
fi
