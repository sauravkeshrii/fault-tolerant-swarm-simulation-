<div align="center">

# ⚓ SWAVLAMBAN 2025: Naval-Grade Swarm Intelligence
### **Distributed Algorithm for Communications-Denied Environments**

![Naval Swarm Banner](Logo.jpg)

[![Challenge](https://img.shields.io/badge/Challenge-Distributed_Swarm-blue.svg)]()
[![Network](https://img.shields.io/badge/Network-60%25_Packet_Loss-red.svg)]()
[![Status](https://img.shields.io/badge/Status-BATTLE_READY-green.svg)]()

</div>

---

## ⚡ Mission Overview

In high-intensity maritime operations, centralized command is a liability. This repository provides a **Hardened Distributed Swarm Algorithm** designed to maintain mission continuity in the face of **60% packet loss** and **active attrition warfare**.

Built for the **Swavlamban 2025 Hackathon**, this solution ensures that 10+ heterogeneous robots can coordinate tasks, elect leaders, and survive continuous node failures without any external server or "God-view".

---

## �️ Elite Features

### 🌪️ Raft-Lite Leader Election (Term-Based)
Traditional elections fail when "zombie" nodes reappear after a network lapse. Our **Epoch/Term** system ensures:
- **Zero Confusion**: Agents only obey the latest Term.
- **Rapid Failover**: New leader emerges in **< 2.5 seconds** when a crash is detected.
- **Conflict Resolution**: Deterministic ID-based "Bully" protocol for identical Terms.

### 📡 Probabilistic Gossip Tasking
When the network is jammed, a single "Assign" command isn't enough. 
- **Persistence**: The Leader uses a 40% probability gossip loop to "re-whisper" active assignments.
- **Reliability**: 10/10 Robots confirmed task completion even under **extreme stress tests**.

### 🔒 Operational Stability Locks
Prevents "Task Flip-Flopping" during network jitters. 
- Assignments are **HARD LOCKED** for 60s (`TASK_STABILITY_TIME`).
- Robots commit to their objective even if they momentarily lose contact with the fleet.

---

## 🎥 Tactical Radar Visualizer

Witness the swarm in action. The visualizer simulates an **Attrition Warfare** scenario where leaders are systematically "killed" (removed) every 20-40 seconds.

```bash
# Run the real-time naval tactical display
python verify_visual.py
```

### **Fleet Capabilities Represented:**
| Asset Class | Symbol | Asset Class | Symbol |
| :--- | :--- | :--- | :--- |
| **Optical Camera** | `C` | **Thermal Sensor** | `T` |
| **LIDAR System** | `L` | **Acoustic Sensor** | `A` |
| **Manipulator Arm** | `M` | **Electronic Scanner** | `E` |
| **Payload Delivery**| `P` | **Defensive Module** | `D` |

---

## 📊 Verification Results

| Scenario | Objective | Stress Level | Result |
| :--- | :--- | :--- | :--- |
| **Leader Stability** | Single stable leader emergence | Low | ✅ **PASSED** |
| **Kill Chain** | Crash recovery < 3.0s | High | ✅ **PASSED** |
| **Scalability** | 10 Assets (Heterogeneous) | Variable | ✅ **PASSED** |
| **Electronic Warfare**| 60% Packet Loss / Jamming | Extreme | ✅ **PASSED** |

---

## 🏗️ Technical Architecture

### **Naval-Grade Logic (agent.py)**
The core agent is a **Finite State Machine (FSM)** designed for predictability:
1.  **`tick`**: Global clock synchronization.
2.  **`receive`**: High-speed inbox processing.
3.  **`elect`**: Decoupled leader logic.
4.  **`assign`**: Gossip-based task distribution.
5.  **`work`**: Async execution with completion callbacks.

### **Telemetry & Black Box**
Every agent generates tagged logs for post-mission analysis:
- `[INFO] (Id: 1) Term 3: I am now the LEADER.`
- `[WARN] (Id: 4) Conflict! Yielding to higher term Leader 1.`

---

## 🚀 Getting Started

1.  **Clone the Mission Data:**
    ```bash
    git clone [repository-url]
    cd Naval-Hackathons
    ```

2.  **Run Stress Tests:**
    ```bash
    python verify_stress.py  # 60% Packet Loss verification
    python verify_failure.py # Leader Crash verification
    ```

3.  **Launch the Visualizer:**
    ```bash
    python verify_visual.py
    ```

---

<div align="center">
<b>Developed for SWAVLAMBAN 2025 - Swarm Algorithm Challenge ⚓</b>
</div>

