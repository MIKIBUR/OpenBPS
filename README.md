# OpenPBS Job Execution Setup

This project uses OpenPBS inside a Docker container to run batch processing jobs via `qsub`.

## ✅ Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

## 🚀 Getting Started

1. **Clone the repository**

2. **Start the container with Docker Compose**:

 ```bash
docker compose up -d
 ```

3. **Enter the running container**:

 ```bash
docker exec -it openpbs bash
 ```
4. **Switch to the pbsuser user**:
 ```bash
su - pbsuser
 ```
5. **Run the PBS script**:
 ```bash
qsub project/calc.pbs
 ```
