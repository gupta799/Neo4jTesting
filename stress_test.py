import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase, basic_auth
import matplotlib.pyplot as plt
import threading
import numpy as np
import seaborn as sns  # For enhanced plotting

# Configuration
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "testabc1234$"

NUM_THREADS = 10
NUM_OPERATIONS = 1000

# Initialize Neo4j Driver
driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))

# Metrics storage
metrics = {
    'write_times': [],
    'read_times': [],
    'write_errors': 0,
    'read_errors': 0,
    'write_count': 0,
    'read_count': 0,
    'write_timestamps': [],
    'read_timestamps': []
}
metrics_lock = threading.Lock()

def create_node(tx, label, properties):
    query = f"CREATE (n:{label} $props) RETURN id(n)"
    result = tx.run(query, props=properties)
    return result.single()[0]

def create_relationship(tx, start_id, end_id, rel_type):
    query = (
        "MATCH (a), (b) "
        "WHERE id(a) = $start_id AND id(b) = $end_id "
        "CREATE (a)-[r:" + rel_type + "]->(b) "
        "RETURN type(r)"
    )
    result = tx.run(query, start_id=start_id, end_id=end_id)
    return result.single()[0]

def read_node(tx, node_id):
    query = "MATCH (n) WHERE id(n) = $id RETURN n"
    result = tx.run(query, id=node_id)
    return result.single()

def perform_write_operations(thread_id, num_ops, start_time):
    with driver.session() as session:
        for i in range(num_ops):
            label = f"Label_{random.randint(1, 10)}"
            properties = {"name": f"Node_{thread_id}_{i}", "value": random.randint(1, 1000)}
            op_start_time = time.time()
            try:
                node_id = session.write_transaction(create_node, label, properties)
                elapsed = time.time() - op_start_time
                with metrics_lock:
                    metrics['write_times'].append(elapsed)
                    metrics['write_count'] += 1
                    metrics['write_timestamps'].append(time.time() - start_time)
                
                # Optionally create relationships
                if i % 10 == 0:  # Every 10th node, create a relationship
                    target_id = random.randint(1, node_id)  # Simple logic to pick a target
                    if target_id < node_id:
                        try:
                            session.write_transaction(create_relationship, node_id, target_id, "RELATED_TO")
                        except Exception as e:
                            # Handle cases where target_id might not exist
                            with metrics_lock:
                                metrics['write_errors'] += 1
            except Exception as e:
                with metrics_lock:
                    metrics['write_errors'] += 1

def perform_read_operations(thread_id, num_ops, start_time):
    with driver.session() as session:
        for i in range(num_ops):
            node_id = random.randint(1, NUM_OPERATIONS)
            op_start_time = time.time()
            try:
                node = session.read_transaction(read_node, node_id)
                elapsed = time.time() - op_start_time
                with metrics_lock:
                    metrics['read_times'].append(elapsed)
                    metrics['read_count'] += 1
                    metrics['read_timestamps'].append(time.time() - start_time)
                # You can process the node if needed
            except Exception as e:
                with metrics_lock:
                    metrics['read_errors'] += 1

def stress_test():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for thread_id in range(NUM_THREADS):
            futures.append(executor.submit(perform_write_operations, thread_id, NUM_OPERATIONS, start_time))
            futures.append(executor.submit(perform_read_operations, thread_id, NUM_OPERATIONS, start_time))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error during stress test: {e}")
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Stress test completed in {total_time:.2f} seconds")
    return total_time, start_time

def plot_metrics(total_time, start_time):
    # Convert timestamps to relative time in seconds
    write_timestamps = metrics['write_timestamps']
    read_timestamps = metrics['read_timestamps']
    
    # Calculate Throughput
    write_throughput = metrics['write_count'] / total_time
    read_throughput = metrics['read_count'] / total_time
    
    print(f"Write Throughput: {write_throughput:.2f} ops/sec")
    print(f"Read Throughput: {read_throughput:.2f} ops/sec")
    
    # Calculate Latency Percentiles
    write_percentiles = np.percentile(metrics['write_times'], [50, 90, 95, 99])
    read_percentiles = np.percentile(metrics['read_times'], [50, 90, 95, 99])
    
    print("Write Latency Percentiles (in seconds):")
    print(f"  50th: {write_percentiles[0]:.4f}")
    print(f"  90th: {write_percentiles[1]:.4f}")
    print(f"  95th: {write_percentiles[2]:.4f}")
    print(f"  99th: {write_percentiles[3]:.4f}")
    
    print("Read Latency Percentiles (in seconds):")
    print(f"  50th: {read_percentiles[0]:.4f}")
    print(f"  90th: {read_percentiles[1]:.4f}")
    print(f"  95th: {read_percentiles[2]:.4f}")
    print(f"  99th: {read_percentiles[3]:.4f}")
    
    # Set a smaller figure size for better visibility
    plt.figure(figsize=(18, 10))
    
    # Plot Write Times Histogram
    plt.subplot(2, 3, 1)
    plt.hist(metrics['write_times'], bins=50, color='blue', alpha=0.7)
    plt.title('Distribution of Write Operation Times')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    
    # Plot Read Times Histogram
    plt.subplot(2, 3, 2)
    plt.hist(metrics['read_times'], bins=50, color='green', alpha=0.7)
    plt.title('Distribution of Read Operation Times')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    
    # Plot Write Latency Box Plot with Strip Plot
    plt.subplot(2, 3, 3)
    sns.boxplot(x=metrics['write_times'], color='lightblue')
    sns.stripplot(x=metrics['write_times'], color='blue', alpha=0.3, jitter=True, size=2)
    plt.title('Box Plot of Write Operation Times')
    plt.xlabel('Time (seconds)')
    
    # Plot Read Latency Box Plot with Strip Plot
    plt.subplot(2, 3, 4)
    sns.boxplot(x=metrics['read_times'], color='lightgreen')
    sns.stripplot(x=metrics['read_times'], color='green', alpha=0.3, jitter=True, size=2)
    plt.title('Box Plot of Read Operation Times')
    plt.xlabel('Time (seconds)')
    
    # Plot Throughput
    plt.subplot(2, 3, 5)
    operations = ['Write', 'Read']
    throughput = [write_throughput, read_throughput]
    colors = ['blue', 'green']
    plt.bar(operations, throughput, color=colors, alpha=0.7)
    plt.title('Throughput')
    plt.ylabel('Operations Per Second')
    
    # Plot Cumulative Operations
    plt.subplot(2, 3, 6)
    # Sort the timestamps for accurate cumulative counts
    write_sorted = sorted(metrics['write_timestamps'])
    read_sorted = sorted(metrics['read_timestamps'])
    plt.plot(write_sorted, np.arange(1, len(write_sorted)+1), label='Writes', color='blue')
    plt.plot(read_sorted, np.arange(1, len(read_sorted)+1), label='Reads', color='green')
    plt.title('Cumulative Operations Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Cumulative Count')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Print Error Counts
    print(f"Write Errors: {metrics['write_errors']}")
    print(f"Read Errors: {metrics['read_errors']}")

if __name__ == "__main__":
    try:
        total_time, start_time = stress_test()
        plot_metrics(total_time, start_time)
    finally:
        driver.close()
