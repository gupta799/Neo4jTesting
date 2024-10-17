# Introduction
The Neo4j Stress Test Tool is a Python-based application designed to evaluate the performance and robustness of Neo4j graph databases under heavy load. By simulating concurrent read and write operations, this tool helps developers and database administrators identify performance bottlenecks, assess throughput, and ensure data integrity in their Neo4j deployments.

## Features
- Multi-Threaded Operations: Simulate concurrent clients performing read and write operations using Python's ThreadPoolExecutor.
- Comprehensive Metrics Collection: Track operation times, error counts, and throughput to gain insights into database performance.
- Advanced Visualizations: Generate detailed histograms, box plots, throughput charts, and cumulative operation graphs using Matplotlib and Seaborn.
- Latency Analysis: Analyze latency percentiles (50th, 90th, 95th, 99th) to understand the distribution of operation response times.
- Error Handling: Monitor and report read and write errors encountered during the stress test.
- Customizable Parameters: Easily adjust the number of threads and operations to tailor the stress test to specific needs.

## Prerequisites
Before setting up and running the Neo4j Stress Test Tool, ensure you have the following:
Python 3.6 or higher
Docker: Installed and running on your system. Refer to the Docker Installation Guide for setup instructions.
Python Packages: Listed in the Installation section.

### Using Docker
Setting up Neo4j using Docker simplifies the installation process and ensures a consistent environment. Follow these steps to get Neo4j running in a Docker container:

Install Docker

If you haven't installed Docker yet, download and install it from the official Docker website.
Pull the Official Neo4j Docker Image
Open your terminal or command prompt and execute:
```bash
docker pull neo4j:latest
```
This command pulls the latest stable version of Neo4j from Docker Hub.

Run Neo4j Container
Start a new Neo4j container with the following command:
```bash
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/testabc1234$ \
    -v neo4j_data:/data \
    neo4j:latest
```
run the python script and see the results
```bash
stress_test.py
```
