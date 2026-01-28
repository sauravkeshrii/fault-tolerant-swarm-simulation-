from agent import Agent, Role
from test_env import LossyEnv
import random
import time

def run_stress_test():
    print("--- NAVAL GRADE STRESS TEST (60% Packet Loss) ---")
    
    # 1. Setup High Chaos Environment
    env = LossyEnv(drop_prob=0.6) 
    agents = [
        Agent(1, "camera", env),
        Agent(2, "camera", env),
        Agent(3, "lidar", env),
        Agent(4, "lidar", env) 
    ]
    
    # Register & Position
    for a in agents:
        env.register(a.id)
        # Random positions 0-20
        env.positions[a.id] = (random.uniform(0, 20), random.uniform(0, 20))
        env.capabilities[a.id] = a.capability

    print(f"Initialized {len(agents)} agents. Starting Chaos...")

    # 2. Run for extended duration
    # We want to see if a leader emerges despite 60% loss
    for i in range(100):
        for a in agents: a.step()
        env.tick()
        
        if i % 10 == 0:
            leaders = [a.id for a in agents if a.role == Role.LEADER]
            terms = [a.term for a in agents]
            print(f"Step {i}: Leaders={leaders}, Terms={terms}")

    # 3. Inject Task in middle of chaos
    print("\n[INJECT] High Priority Lidar Task")
    env.send({
        "type": "TASK_NEW",
        "task": {
            "id": 999,
            "location": (10, 10),
            "capability": "lidar",
            "deadline": 200.0,
            "assigned_to": None,
            "locked": False
        }
    })

    # 4. Resolve
    for i in range(100):
        for a in agents: a.step()
        env.tick()

    # 5. Report
    completed_count = 0
    for a in agents:
        if a.known_tasks.get(999, {}).get("completed"):
            completed_count += 1
            
    print(f"\n--- REPORT ---")
    print(f"Agents with Task Completed: {completed_count}/{len(agents)}")
    
    leaders = [a.id for a in agents if a.role == Role.LEADER]
    print(f"Final Leaders: {leaders}")
    
    if completed_count > 0:
        print("PASS: Task completed despite chaos.")
    else:
        print("FAIL: Task succumbed to chaos.")

if __name__ == "__main__":
    run_stress_test()