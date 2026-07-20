# Cristian's Clock Synchronization Algorithm

Implementation and evaluation of Cristian's Algorithm for clock synchronization across distributed systems. Each activity investigates a different aspect of the algorithm's behavior under various conditions.

## Prerequisites

```bash
pip install matplotlib
```

All scripts use only the Python standard library plus `matplotlib` for plotting.

---

## Project Structure

```
cristian.py                 # Base server (port 8080, 100ms delay)
server_activity3.py         # Configurable-delay server (Activity 3)
server_activity5.py         # Configurable port + delay server (Activities 5-7)
client.py                   # Basic Cristian sync demo (Activity 1)
client_activity2.py         # Packet loss simulation
client_activity3.py         # Variable server processing time
client_activity4.py         # Clock drift over time
client_activity5.py         # Multiple time servers
client_activity6.py         # Performance analysis
client_activity7.py         # Enhanced synchronization strategies
```

---

## Activity 1: Basic Cristian's Algorithm

**Files:** `cristian.py` + `client.py`

Demonstrates the core Cristian's Algorithm. The client starts with a random clock offset (-1 to +1 hour), sends a request to the server, receives the server's time, and computes the synchronized time.

### How it works

1. Client records timestamp `T0` (with random offset)
2. Client sends request to server
3. Server records its time `T1` and sends it back
4. Client records timestamp `T2` upon receiving the response
5. Client computes: `RTT = T2 - T0`
6. Client computes: `synchronized_time = T1 + RTT/2`

### How to run

```bash
# Terminal 1 - start the server
python cristian.py

# Terminal 2 - run the client
python client.py
```

### Output

Prints all recorded values to the console:
- Initial client clock (T0)
- Server time (T1)
- Request time (T0)
- Response time (T2)
- Round-trip delay (RTT)
- Clock adjustment
- Final synchronized clock
- Synchronization error

Generates `cristian_clock.png` with a timeline diagram and clock comparison bar chart.

---

## Activity 2: Packet Loss Simulation

**Files:** `cristian.py` + `client_activity2.py`

Simulates packet loss at rates of 0%, 5%, 10%, and 20%. When a packet is lost, the client closes the connection, opens a new one, and retransmits (up to 5 retries per trial).

### How it works

For each loss rate, 100 synchronization trials are run. Packet loss is simulated by:
- Randomly discarding the request before sending
- Randomly discarding the response after receiving
- Timeouts when the server never responds

### Measured metrics

| Metric | Description |
|--------|-------------|
| Successful synchronizations | Trials that completed within 5 retries |
| Retransmissions | Total retransmission attempts across all trials |
| Average synchronization error | Mean error from real time for successful syncs |

### How to run

```bash
# Terminal 1 - start the server
python cristian.py

# Terminal 2 - run the client
python client_activity2.py
```

### Output

Console summary for each loss rate plus `packet_loss_results.png` with three bar charts.

---

## Activity 3: Variable Server Processing Time

**Files:** `server_activity3.py` + `client_activity3.py`

Tests how server processing delay affects synchronization accuracy. The client automatically starts and stops the server with different delay configurations.

### Configurations

| Label | Server Delay |
|-------|-------------|
| 10ms | 0.01 seconds |
| 100ms | 0.1 seconds |
| 500ms | 0.5 seconds |

### How it works

The client uses `subprocess` to start `server_activity3.py` with a command-line delay argument, runs 100 synchronization trials, then stops the server before moving to the next configuration.

### Measured metrics

- Successful synchronizations
- Average RTT (includes server processing time)
- Average/Min/Max synchronization error

### How to run

```bash
python client_activity3.py
```

The server starts and stops automatically. No manual server startup needed.

### Output

Console summary per delay plus `server_delay_results.png` with three bar charts.

### Key insight

Larger server delays increase RTT, which increases the uncertainty in the one-way delay estimate (`RTT/2`), leading to larger synchronization errors.

---

## Activity 4: Clock Drift Over Time

**Files:** `cristian.py` + `client_activity4.py`

Simulates clock drift by gradually adjusting the client's clock offset over time before synchronizing. Tests drift periods of 0, 30, 60, 120, and 300 seconds.

### How it works

1. Client starts with a random base offset
2. For each drift period, the offset increases at `0.05 seconds/second`
3. After the drift period, the client synchronizes with the server
4. Drift accumulated, correction applied, and sync error are recorded

### Drift rate

The simulated drift rate is 50 ppm (parts per million), which is typical for inexpensive crystal oscillators. Over 300 seconds, this accumulates ~15 seconds of drift.

### Measured metrics

| Metric | Description |
|--------|-------------|
| Drift accumulated | Total clock drift before synchronization |
| Correction applied | Adjustment the algorithm computed |
| Synchronization error | Difference between synchronized time and real time |

### How to run

```bash
python client_activity4.py
```

The server starts and stops automatically.

### Output

Console summary per drift period plus `drift_results.png`.

---

## Activity 5: Multiple Time Servers

**Files:** `server_activity5.py` + `client_activity5.py`

Deploys two time servers with different processing delays and compares three server selection strategies.

### Server configuration

| Server | Port | Delay |
|--------|------|-------|
| fast | 8081 | 10ms |
| slow | 8082 | 150ms |

### Strategies compared

| Strategy | Description |
|----------|-------------|
| Nearest | Selects the server with the lowest RTT |
| Least Loaded | Selects the server with the latest timestamp (most processing time = least queued work) |
| Average | Queries both servers and averages the results |

### How to run

```bash
python client_activity5.py
```

Both servers start and stop automatically.

### Output

Console summary per strategy plus `multi_server_results.png` with three bar charts comparing success rate, RTT, and sync error.

---

## Activity 6: Performance Analysis

**Files:** `server_activity5.py` + `client_activity6.py`

Comprehensive performance benchmarking across three server configurations. Measures synchronization time, network traffic, CPU utilization, and accuracy.

### Configurations

| Config | Port | Delay |
|--------|------|-------|
| Fast | 8081 | 10ms |
| Medium | 8082 | 100ms |
| Slow | 8083 | 500ms |

### Measured metrics

| Metric | Source |
|--------|--------|
| Synchronization time | `(T2 - T0)` per trial |
| Network traffic | Bytes sent/received per sync + `/proc/net/dev` |
| CPU utilization | `/proc/stat` before and after trials |
| Synchronization error | `abs(synchronized_time - real_time)` |
| Throughput | Successful syncs per second |

### How to run

```bash
python client_activity6.py
```

All servers start and stop automatically.

### Output

Console summary per config, a formatted comparison table, and `performance_results.png` with 6 panels (5 bar charts + 1 summary table).

---

## Activity 7: Enhanced Synchronization Strategy

**Files:** `server_activity5.py` + `client_activity7.py`

Implements six synchronization strategies and compares them against the original Cristian's Algorithm. Uses three servers with different delays (10ms, 50ms, 200ms).

### Strategies

| Strategy | Description | Messages/Sync |
|----------|-------------|---------------|
| Original Cristian | Single server, single request | 1 |
| Multi-Server Best | Queries all servers, picks the one with lowest error | 3 |
| Multi-Server Avg | Queries all servers 5 times, averages adjustments | 15 |
| RTT Filter | Queries all servers, rejects responses with RTT > 500ms | 3 |
| Drift Prediction | Takes 3 measurements, predicts future drift | 3 |
| Weighted Average | Queries all servers, weights by inverse RTT | 3 |

### Enhancements explained

**Multi-Server Best:** Queries all available servers and selects the response with the lowest synchronization error. Provides redundancy and better accuracy through selection.

**Multi-Server Averaging:** Sends multiple requests to all servers and averages the adjustments. Reduces the impact of individual measurement noise at the cost of more network traffic.

**RTT Filter:** Rejects any server response where the round-trip time exceeds a threshold (500ms). Filters out responses that likely suffered from network congestion or queuing delays.

**Drift Prediction:** Takes multiple time measurements, computes the drift rate, and predicts what the adjustment should be at a future point. Useful when synchronization intervals are irregular.

**Weighted Average:** Combines responses from all servers, weighting each by the inverse of its RTT. Servers with lower latency (and thus more reliable one-way delay estimates) contribute more to the final result.

### Measured metrics

| Metric | Description |
|--------|-------------|
| Synchronization accuracy | Mean error from real time |
| Messages per sync | Average network messages required |
| Response time | Average RTT |
| Fault tolerance | Percentage of successful syncs |

### How to run

```bash
python client_activity7.py
```

All three servers start and stop automatically.

### Output

Console summary per strategy, a comparison table with fault tolerance rating, and `enhanced_strategy_results.png` with 4 horizontal bar charts.

---

## Algorithm Reference

Cristian's Algorithm estimates the correct time as:

```
Synchronized Time = T1 + RTT / 2
```

Where:
- `T0` = client timestamp before sending request
- `T1` = server timestamp when processing request
- `T2` = client timestamp after receiving response
- `RTT = T2 - T0` (round-trip time)
- Estimated one-way delay = `RTT / 2`

The adjustment applied to the client clock is:

```
adjustment = (T1 - T0) + RTT / 2
synchronized_time = T0 + adjustment
```

### Assumptions

- Network latency is symmetric (forward delay = reverse delay)
- The server's clock is accurate (reference clock)
- Clock drift is negligible during a single synchronization exchange

### Limitations

- Accuracy is bounded by `RTT/2` (minimum possible error)
- Asymmetric network paths degrade accuracy
- Server processing time adds to RTT and increases uncertainty
- No protection against faulty or malicious time servers
