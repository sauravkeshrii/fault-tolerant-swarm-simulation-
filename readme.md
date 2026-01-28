# Naval Grade Swarm Agent - SWAVLAMBAN 2025

**Challenge 1: Distributed Swarm Algorithm**

This repository contains a **Naval Grade** implementation of a distributed swarm algorithm, designed for high reliability, fault tolerance, and operation in communications-denied environments (60% packet loss).

## 🚀 Key Features

### 1. Robust "Term-Based" Leader Election (Raft-Lite)
- **Problem**: In lossy networks, old leaders ("zombies") can wake up and confuse the fleet.
- **Solution**: We implemented an **Epoch/Term** system. Agents only obey commands from the current term. If a leader fails, a new one is elected in **< 2.5 seconds** automatically.
- **Status**: ✅ PASSED (Verified via `verify_failure.py`)

### 2. Gossip-Based Task Reliability
- **Problem**: 60% Packet Loss means simple commands often fail to reach the worker.
- **Solution**: The Leader uses a probabilistic **Gossip Protocol** to "whisper" active assignments until completion is confirmed.
- **Status**: ✅ PASSED (10/10 Robots completed tasks in stress tests)

### 3. Strict Stability Locks
- **Problem**: Tasks must not "flip-flop" between robots.
- **Solution**: Assignments are **HARD LOCKED** for 60 seconds (`TASK_STABILITY_TIME`), ensuring commitment even if network conditions fluctuate.

## 📂 Repository Structure

- **`agent.py`**: 🧠 **THE SOLUTION**. The core logic for every robot.
- `verify_scale.py`: verification script for 10-robot scalability.
- `verify_failure.py`: verification script for Leader Crash recovery.
- `verify_stress.py`: verification script for 60% Packet Loss.
- **`verify_visual.py`**: 🎥 **RADAR VISUALIZER**. Runs a real-time ASCII simulation for recording the demo video.

## 🛠️ Design Philosophy

We adhered to a **"Zero-Magic"** principle:
1.  **No Central Server**: Every agent runs identical code.
2.  **Stateless Recovery**: Any robot can reboot and rejoin instantly.
3.  **Low Bandwidth**: Event-driven architecture (only speaks when necessary).

## 📊 Verification Results

| Test Case | Scenario | Result |
| :--- | :--- | :--- |
| **Leader Stability** | Single Leader emerged | ✅ PASS |
| **Fail-Over** | Leader Killed -> New Leader < 3s | ✅ PASS |
| **Scalability** | 10 Robots (5 Cam, 5 Lidar) | ✅ PASS |
| **Jamming** | 60% Packet Loss Survival | ✅ PASS |


## 🏗️ Technical Architecture

### Core Components
*   **Role Management**: Strict `IntEnum` for roles (Leader/Follower) avoids string parsing errors.
*   **Finite State Machine (FSM)**: Agent logic is divided into distinct phases (`tick` -> `receive` -> `heartbeat` -> `elect` -> `work`) to prevent race conditions.
*   **Type Safety**: All methods utilize Python `typing` hints (`List[int]`, `Dict`) for maintainability.

### "Black Box" Telemetry
The agent includes a built-in `logging` system that outputs tagged logs (e.g., `[INFO] (Id: 1) Term 2: Leader Elected`). This allows for post-mission analysis of:
- Election timing
- Conflict resolution events
- Task assignment logic loops
