---
title: Cristian Clock Synchronization
author: Group 3
theme:
  name: dark
  override:
    default:
      title:
        font_size: 3
      colors:
        background: "09090F"
        foreground: "EBDBB2"
    code:
      theme_name: gruvbox-dark
      padding:
        horizontal: 2
        vertical: 1
      background: false
    palette:
      colors:
        black: "282828"
        red: "CC241D"
        green: "98971A"
        yellow: "D79921"
        blue: "458588"
        purple: "B16286"
        aqua: "689D6A"
        orange: "D65D0E"
        gray: "A89984"
        light_red: "FB4934"
        light_green: "B8BB26"
        light_yellow: "FABD2F"
        light_blue: "83A598"
        light_purple: "D3869B"
        light_aqua: "8EC07C"
        light_orange: "FE8019"

---
How the Algorithm Works.
---
1. **Request:** A client process P records its current local time as T₀ and sends a time request message to the server S.
2. **Response:** The time server S receives the request, processes it, and replies with a message containing its own current clock time
```latex +render +no_background
\(T_{server}\).
```

3. **Receipt:** The client P receives the response message and immediately records its local time as T₁.
4. **Calculation:** The client calculates the total Round-Trip Time:
```latex +render +no_background
\(\text{RTT}=T_{1}-T_{0}\)
```
5. **Synchronization:** Assuming network delays are symmetrical (the request and response took equal time), the time taken for the response to travel back to the client is: 
```latex +render +no_background
\(\frac{\text{RTT}}{2}\). 
```
<!-- end_slide -->

Finally The client updates its clock to:
---
```latex +render +no_background
\(T_{\text{new}}=T_{server}+\frac{\text{RTT}}{2}\)
```

<!-- end_slide -->

Activity 0: Basic Cristian's Algorithm
---

Demonstrates the core Cristian's Algorithm. The client starts with a random clock offset (-1 to +1 hour), sends a request to the server, receives the server's time, and computes the synchronized time.

<!-- end_slide -->

Activity 1: Synchronization Frequency Study
---
Perform synchronization every: 1 second, 5 seconds, 10 seconds, 30 seconds
Compare synchronization accuracy and communication overhead.

<!-- end_slide -->

Activity 2: Packet Loss Simulation
---
Simulates packet loss at rates of 0%, 5%, 10%, and 20%. When a packet is lost, the client closes the connection, opens a new one, and retransmits (up to 5 retries per trial).

<!-- end_slide -->

Activity 3: Variable Server Processing Time
---
Tests how server processing delay affects synchronization accuracy. The server to delays responses by: 10 ms, 100 ms, 500 ms
<!-- end_slide -->

Activity 4: Variable Server Processing Time
---

Simulates clock drift by gradually adjusting the client's clock offset over time before synchronizing. Tests drift periods of 0, 30, 60, 120, and 300 seconds.
<!-- end_slide -->

Activity 5: Multiple Time Servers
---
Deploys two time servers with different processing delays and compares three server selection strategies.

| Strategy     | Description                                                                             |
| ------------ | --------------------------------------------------------------------------------------- |
| Nearest      | Selects the server with the lowest RTT                                                  |
| Least Loaded | Selects the server with the latest timestamp (most processing time = least queued work) |
| Average      | Queries both servers and averages the results                                           |
<!-- end_slide -->

Activity 6: Performance Analysis
---

| Metric | Source |
|--------|--------|
| Synchronization time | `(T2 - T0)` per trial |
| Network traffic | Bytes sent/received per sync + `/proc/net/dev` |
| CPU utilization | `/proc/stat` before and after trials |
| Synchronization error | `abs(synchronized_time - real_time)` |
| Throughput | Successful syncs per second |

<!-- end_slide -->

Activity 7: Enhanced Synchronization Strategy
---
**Multi-Server Best:** Queries all available servers and selects the response with the lowest synchronization error. Provides redundancy and better accuracy through selection.

<!-- end_slide -->

Limitations
---
- Accuracy is bounded by `RTT/2` (minimum possible error)
- Asymmetric network paths degrade accuracy
- Server processing time adds to RTT and increases uncertainty
- No protection against faulty or malicious time servers

<!-- end_slide -->

Berkeley's Algorithm
---

Berkeley algorithm is a distributed, internal method where a central coordinator polls nodes, calculates an average time to reach consensus, and adjusts clocks internally without needing an external reference.


<!-- end_slide -->
Cristian's Algorithm vs. Berkeley Algorithm
---
 
## Time Source
 
- **Cristian's:** Synchronizes with a highly accurate external Time Server (e.g., UTC).
- **Berkeley:** Assumes no single machine is perfectly accurate. Uses an average of all clocks in the network.
<!-- pause -->
## Architecture
 
- **Cristian's:** Client-server model.
- **Berkeley:** Master-slave (Coordinator-follower) model.
<!-- pause -->
## Fault Tolerance
 
- **Cristian's:** Low. If the single Time Server fails, the entire system cannot synchronize.
- **Berkeley:** High. If the master fails, the system can elect a new master to continue synchronizing.
<!-- end_slide -->
## Accuracy
 
- **Cristian's:** High. Synchronizes to real-world time (UTC).
- **Berkeley:** Can drift from real-world time, but highly consistent internally, minimizing maximum clock drift between nodes.
<!-- pause -->
## Use Case
 
- **Cristian's:** Systems requiring an accurate external time reference (e.g., specific databases, web servers).
- **Berkeley:** Local Area Networks (LANs) / intranets with mutually trusting nodes that just need to remain strictly consistent with each other.
---
<!-- end_slide -->

The end
---
