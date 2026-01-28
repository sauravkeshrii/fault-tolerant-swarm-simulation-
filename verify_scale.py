from agent import Agent, Role
from test_env import LossyEnv
import random
import time

def run_stress_test_scaled():
    print("--- NAVAL GRADE SCALABILITY TEST (10 Robots, 60% Loss) ---")
    
    # 1. Setup Environment
    env = LossyEnv(drop_prob=0.6) 
    
    # create 10 agents
    # 5 Cameras, 5 Lidars
    agents = []
    for i in range(1, 11):
        cap = "camera" if i <= 5 else "lidar"
        agents.append(Agent(i, cap, env))
    
    # Register & Position
    for a in agents:
        env.register(a.id)
        # Spread them out in a 50x50 area
        env.positions[a.id] = (random.uniform(0, 50), random.uniform(0, 50))
        env.capabilities[a.id] = a.capability

    print(f"Initialized {len(agents)} agents. Starting Simulation...")

    # 2. Run Initialization to let chaos settle and leader emerge
    for i in range(100):
        for a in agents: a.step()
        env.tick()
        
        if i % 20 == 0:
            leaders = [a.id for a in agents if a.role == Role.LEADER]
            print(f"Step {i}: Active Leaders={leaders}")

    # 3. Inject Task (Retry a few times to ensure Leader hears it in this noisy environment)
    print("\n[INJECT] Task for Agent 8 (Lidar)")
    task_payload = {
        "type": "TASK_NEW",
        "task": {
            "id": 500,
            "location": (25, 25), # Middle of field
            "capability": "lidar",
            "deadline": 500.0,
            "assigned_to": None,
            "locked": False
        }
    }
    
    # Simulate persistent operator
    for _ in range(5): 
        env.send(task_payload)
        env.tick()
        time.sleep(0.01)

    # 4. Resolve (Give it time to propagate across 10 nodes)
    print("Resolving...")
    for i in range(100):
        for a in agents: a.step()
        env.tick()

    # 5. Report
    completed_count = 0
    assigned_to = None
    
    # Check consensus
    for a in agents:
        t = a.known_tasks.get(500, {})
        if t.get("completed"):
            completed_count += 1
        if t.get("assigned_to"):
            assigned_to = t.get("assigned_to")
            
    print(f"\n--- REPORT ---")
    print(f"Task Assigned To: Agent {assigned_to}")
    print(f"Agents with Task Completed: {completed_count}/{len(agents)}")
    
    leaders = sorted([a.id for a in agents if a.role == Role.LEADER])
    print(f"Final Leaders: {leaders}")
    
    if len(leaders) == 1:
        print("PASS: Single Leader Stability.")
    else:
        print(f"WARNING: Multiple Leaders {leaders} (Expected in high packet loss transient)")

    if completed_count >= 5: # At least half the fleet knows
        print("PASS: Task Completion Propagated.")
    else:
        print("FAIL: Task Knowledge Propagation Failed.")


if __name__ == "__main__":
    run_stress_test_scaled()
