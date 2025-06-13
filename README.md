# 🚧 OpenPBS Job Execution Setup

This project demonstrates how to use **OpenPBS** within a **Docker container** to run batch processing jobs using `qsub`, and `mpiexec`. It includes a wrapper script (`run.sh`) to easily configure and launch jobs with custom parameters. The pararrel task wich is subject of this presentation is monte carlo integration technique.

## ✅ Prerequisites

Before you begin, ensure the following tools are installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Getting Started

1. **Clone the repository:**

    ```bash
    git clone https://github.com/MIKIBUR/OpenBPS.git
    cd OpenBPS
    ```

2. **Start the OpenPBS container** using Docker Compose:

   ```bash
   docker compose up -d --build
   ```

3. **Access the running container**:

   ```bash
   docker exec -it openpbs bash
   ```

4. **Run a batch job using the helper script**:

   ```bash
   ./run.sh <mode> <samples_per_node> <bounds>
   ```

   - `<mode>`: Execution mode – either `''` (empty) for native OpenPBS or `'mpi'` for MPI-based parallel execution.
   - `<samples_per_node>`: Number of samples each node should process.
   - `<bounds>`: A comma-separated tuple of value ranges, e.g., `"(0,1),(0,1)"`.

   **Example**:

   ```bash
   ./run.sh mpi 100000 "(0,1),(0,1)"
   ```

   This submits an MPI job that distributes `100,000` samples per node with the given function bounds.

⚠️ **Disclaimer**:  
The number of nodes used in the job is **not currently parameterized** due to the complexity of configuring multi-node setups in Docker-based environments.  
If you require multiple nodes, you will need to set this up manually within your Docker/OpenPBS configuration.<br>
⚠️ **Disclaimer no. 2**:
When encountering errors connected with entrypoint.sh like this one: 
`exec: "./entrypoint.sh": stat ./entrypoint.sh: no such file or directory: unknown`
Make sure you have linux line endings `LF` in all .sh files as it may cause serious issues!