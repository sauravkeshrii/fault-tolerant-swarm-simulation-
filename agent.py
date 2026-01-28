# -----------------------------------------------------------------------------
# SWAVLAMBAN 2025: Distributed Swarm Algorithm (Naval Grade Implementation)
# -----------------------------------------------------------------------------

import time
import math
import random
import logging
from enum import IntEnum
from typing import Dict, List, Optional, Any, Union, Set

# ------------------ LOGGING ------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (Id: %(name)s) %(message)s')

# ------------------ CONSTANTS ------------------
TICK_HZ = 10
TICK_DT = 1.0 / TICK_HZ

LEADER_TIMEOUT = 2.5          # Seconds before declaring leader dead
TASK_STABILITY_TIME = 60.0    # Seconds to lock a task assignment

# ------------------ ENUMS & TYPES ------------------
class Role(IntEnum):
    FOLLOWER = 0
    LEADER = 1
    CANDIDATE = 2  # Future-proofing for more complex elections

class MsgType:
    HB = "HB"
    TASK_NEW = "TASK_NEW"
    TASK_ASSIGN = "TASK_ASSIGN"
    TASK_DONE = "TASK_DONE"

# ------------------ AGENT ------------------
class Agent:
    def __init__(self, robot_id: int, capability: str, env: Any):
        self.id = robot_id
        self.capability = capability
        self.env = env
        self.logger = logging.getLogger(str(self.id))

        # State
        self.role: Role = Role.FOLLOWER
        self.leader_id: Optional[int] = None
        self.term: int = 0  # Election term (Epoch) for conflict resolution

        # Knowledge Bases
        self.last_seen: Dict[int, float] = {}          # robot_id -> timestamp (local time)
        self.known_tasks: Dict[int, Dict[str, Any]] = {}  # task_id -> task dict
        self.current_task: Optional[int] = None           # ID of task currently being executed

        self.now = self.env.get_time()

    def step(self):
        """Called by simulator once per step."""
        self.tick()

    # ------------------ COMMUNICATION (LAYER 1) ------------------
    def send(self, msg: Dict[str, Any]):
        """Safe wrapper for environment send."""
        # Inject standard headers
        msg["from"] = self.id
        msg["term"] = self.term 
        self.env.send(msg)

    def receive(self) -> List[Dict[str, Any]]:
        """Safe wrapper for environment receive."""
        return self.env.receive(self.id)

    # ------------------ HEARTBEAT PROTOCOL ------------------
    def send_heartbeat(self):
        self.send({
            "type": MsgType.HB,
            "role": int(self.role) # Send role to detect conflicts
        })

    def handle_heartbeat(self, msg: Dict[str, Any]):
        sender = msg["from"]
        remote_term = msg.get("term", 0)
        remote_role = Role(msg.get("role", Role.FOLLOWER))

        # Term Check: Join higher term if we are behind
        if remote_term > self.term:
            self.term = remote_term
            self.role = Role.FOLLOWER
            self.leader_id = None # Reset, wait for new leader data

        # Liveness update
        self.last_seen[sender] = self.now

        # Conflict Resolution: Two leaders?
        if self.role == Role.LEADER and remote_role == Role.LEADER and sender != self.id:
            # 1. Term Priority
            if remote_term > self.term:
                self.logger.warning(f"Conflict! Yielding to higher term Leader {sender}")
                self.role = Role.FOLLOWER
                self.term = remote_term
                self.leader_id = sender
                return

            # 2. ID Priority (Bully) - Lower ID Wins
            if remote_term == self.term:
                if sender < self.id:
                    self.logger.warning(f"Conflict! Yielding to lower ID Leader {sender}")
                    self.role = Role.FOLLOWER
                    self.leader_id = sender
                else:
                    # I am the superior leader. I stay leader. 
                    # The other guy should yield when he hears me.
                    pass
    
    # ------------------ LEADER ELECTION ------------------
    def detect_leader_failure(self) -> bool:
        if self.leader_id is None:
            return True

        last = self.last_seen.get(self.leader_id, 0.0)
        return (self.now - last) > LEADER_TIMEOUT

    def elect_leader(self):
        """
        Deterministic, ID-based election. 
        Only runs if leader is dead or unknown.
        """
        # 1. Who is alive?
        alive = [
            rid for rid, t in self.last_seen.items()
            if (self.now - t) <= LEADER_TIMEOUT
        ]
        alive.append(self.id)
        
        # 2. Who is the best candidate? (Lowest ID)
        new_leader = min(set(alive))

        # 3. Apply Decision
        if new_leader == self.id:
            if self.role != Role.LEADER:
                self.term += 1 # Start new term!
                self.role = Role.LEADER
                self.leader_id = self.id
                self.logger.info(f"Term {self.term}: I am now the LEADER.")
        else:
            self.role = Role.FOLLOWER
            self.leader_id = new_leader

    # ------------------ TASK LOGIC ------------------
    def _scan_neighbors_for_capability(self, capability: str) -> List[int]:
        """Helper to find capable neighbors safely."""
        robots = []
        for r in self.env.get_neighbors():
            if self.env.has_capability(r, capability):
                robots.append(r)
        return robots

    def get_capable_robots(self, capability: str) -> List[int]:
        robots = self._scan_neighbors_for_capability(capability)
        if self.capability == capability:
            robots.append(self.id)
        return robots

    def pick_closest(self, task: Dict, robots: List[int]) -> Optional[int]:
        best = None
        best_dist = float("inf")
        task_loc = task["location"]

        for r in robots:
            pos = self.env.get_position(r)
            if pos is None: continue # Safe check
            
            d = math.dist(pos, task_loc)
            if d < best_dist:
                best_dist = d
                best = r
        return best

    def assign_tasks(self):
        """Leader logic to assign pending tasks."""
        if self.role != Role.LEADER:
            return

        for task in self.known_tasks.values():
            
            # Guard Clauses
            if task.get("completed", False): continue

            # 1. Gossip / Reliability Check (Pre-Lock)
            assigned_id = task.get("assigned_to")
            if assigned_id is not None:
                # Task is assigned. We must ensure they know it.
                # Even if locked, we gossip.
                if random.random() < 0.4: 
                     self.logger.info(f"Re-Gossiping Task {task['id']} to Agent {assigned_id}")
                     self.send({
                        "type": MsgType.TASK_ASSIGN,
                        "task_id": task["id"],
                        "task": task,
                        "to": assigned_id
                    })
                continue

            # 2. Stability Lock (Prevent Re-Assignment thrashing)
            if task.get("locked", False):
                if self.now - task.get("lock_time", 0) < TASK_STABILITY_TIME:
                    continue

            # 3. New Allocation
            candidates = self.get_capable_robots(task["capability"])
            if not candidates: 
                # Only warn occasionally?
                # self.logger.warning(f"No capable candidates for task {task['id']} (cap={task['capability']})")
                continue

            chosen = self.pick_closest(task, candidates)
            if chosen is not None:
                # Update Local Knowledge
                task["assigned_to"] = chosen
                task["lock_time"] = self.now
                task["locked"] = True

                # Broadcast Assignment
                self.logger.info(f"Assigning Task {task['id']} to Agent {chosen}")
                self.send({
                    "type": MsgType.TASK_ASSIGN,
                    "task_id": task["id"],
                    "task": task, 
                    "to": chosen
                })

    def handle_new_task(self, msg: Dict):
        task = msg["task"]
        # Safe merge of task attributes
        if "assigned_to" not in task: 
            task["assigned_to"] = None
        
        # We only accept new info if we don't have it or it's a newer version?
        # For simplicity of this challenge, last-write-wins but respect 'completed'
        if task["id"] not in self.known_tasks:
             self.known_tasks[task["id"]] = task

    def handle_task_assign(self, msg: Dict):
        # Am I the target?
        if msg["to"] == self.id:
            tid = msg["task_id"]
            self.current_task = tid
            # Also update my knowledge of the task
            if "task" in msg:
                self.known_tasks[tid] = msg["task"]
                self.known_tasks[tid]["assigned_to"] = self.id

    def complete_task(self):
        if self.current_task is None: return

        tid = self.current_task
        if tid in self.known_tasks:
            self.known_tasks[tid]["completed"] = True
            
            self.logger.info(f"Task {tid} COMPLETED.")
            self.send({
                "type": MsgType.TASK_DONE,
                "task_id": tid
            })
        
        self.current_task = None

    # ------------------ MAIN LOOP ------------------
    def tick(self):
        self.now = self.env.get_time()

        # 1. Process Inbox
        msgs = self.receive()
        for msg in msgs:
            t = msg.get("type")

            if t == MsgType.HB:
                self.handle_heartbeat(msg)
            elif t == MsgType.TASK_NEW:
                self.handle_new_task(msg)
            elif t == MsgType.TASK_ASSIGN:
                self.handle_task_assign(msg)
            elif t == MsgType.TASK_DONE:
                tid = msg.get("task_id")
                if tid in self.known_tasks:
                    self.known_tasks[tid]["completed"] = True

        # 2. Maintain Life (Throttle: 1Hz Heartbeat)
        if self.now - getattr(self, '_last_hb', 0.0) >= 1.0:
            self.send_heartbeat()
            self._last_hb = self.now

        # 3. Maintain Leadership
        if self.detect_leader_failure():
            self.elect_leader()

        if self.role == Role.LEADER:
            self.assign_tasks()

        # 4. Work
        if self.current_task is not None:
            self.complete_task()

    # ------------------ RUN ------------------
    def run(self):
        while True:
            start = time.time()
            self.last_seen[self.id] = self.now
            self.tick()
            elapsed = time.time() - start
            time.sleep(max(0, TICK_DT - elapsed))
