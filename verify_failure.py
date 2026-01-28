from agent import Agent, Role
from test_env import LossyEnv
import random
import time

def run_failure_demo():
    print("--- NAVAL GRADE FAILURE RECOVERY DEMO ---")
    
    # 1. Setup Environment
    env = LossyEnv(drop_prob=0.0) # Clear comms to show logic clearly
    
    agents = []
    for i in range(1, 11):
        cap = "camera" if i <= 5 else "lidar"
        agents.append(Agent(i, cap, env))
        env.register(i)
        
    print(f"Initialized {len(agents)} agents.")

    # 2. Run until stability (Leader 1 emerges)
    print("\n[PHASE 1] Establishing Leadership...")
    for i in range(30):
        for a in agents: a.step()
        env.tick()
        
    leaders = [a.id for a in agents if a.role == Role.LEADER]
    print(f"Current Leader: {leaders}")

    # 3. KILL THE LEADER
    print("\n[PHASE 2] !!! MURDERING LEADER (ID 1) !!!")
    # We remove Agent 1 from the execution loop. It simulates a crash/destruction.
    alive_agents = agents[1:] # 2 through 10
    
    # 4. Run to see recovery
    print("Running simulation without Leader 1...")
    for i in range(50):
        for a in alive_agents: a.step()
        env.tick()
        
        # Check every 10 steps who is leader
        if i % 10 == 0:
            leaders = [a.id for a in alive_agents if a.role == Role.LEADER]
            print(f"Step {i}: Agents believe Leaders are: {leaders}")

    # 5. Conclusion
    final_leaders = set([a.id for a in alive_agents if a.role == Role.LEADER])
    print(f"\n--- REPORT ---")
    print(f"Original Leader: 1 (Dead)")
    print(f"New Leader: {final_leaders}")
    
    if len(final_leaders) == 1 and 1 not in final_leaders:
        print("PASS: Successfully elected new leader automatically.")
    else:
        print("FAIL: Leadership recovery failed.")

if __name__ == "__main__":
    run_failure_demo()
