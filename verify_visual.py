import os
import time
import sys
from agent import Agent, Role
from test_env import LossyEnv
import random

# ANSI Colors for Naval Aesthetic
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_header(time_elapsed, term):
    print(f"{GREEN}{BOLD}--- SWAVLAMBAN NAVAL TACTICAL DISPLAY ---{RESET}")
    print(f"TIME: {time_elapsed:.1f}s | TERM: {term} | STATUS: {RED}COMBAT (60% LOSS){RESET}")
    print("-" * 60)

def draw_map(agents, task=None, width=50, height=20):
    # Create empty grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Scale factors
    scale_x = width / 50
    scale_y = height / 50

    # Plot Agents
    for a in agents:
        x, y = a.env.get_position(a.id)
        gx = max(0, min(int(x * scale_x), width-1))
        gy = max(0, min(int(y * scale_y), height-1))
        
        symbol = a.capability[0].upper() # Default to first letter
        if "Camera" in a.capability: symbol = 'C'
        elif "LIDAR" in a.capability: symbol = 'L'
        elif "Thermal" in a.capability: symbol = 'T'
        elif "Acoustic" in a.capability: symbol = 'A'
        elif "Manipulator" in a.capability: symbol = 'M'
        
        color = CYAN
        if a.role == Role.LEADER:
            symbol = '★' # Leader Star
            color = YELLOW
            
        # If task assigned
        if task and task.get('assigned_to') == a.id:
            color = GREEN
            symbol = '@' # Working

        grid[gy][gx] = f"{color}{symbol}{RESET}"

    # Plot Task
    if task and not task.get('completed'):
        tx, ty = task['location']
        grid[int(ty*scale_y)][int(tx*scale_x)] = f"{RED}X{RESET}"

    # Render
    print(f"{BLUE}+{'-'*width}+{RESET}")
    for row in grid:
        print(f"{BLUE}|{RESET}" + "".join(row) + f"{BLUE}|{RESET}")
    print(f"{BLUE}+{'-'*width}+{RESET}")

def run_visual_demo():
    # Setup
    env = LossyEnv(drop_prob=0.6)
    agents = []
    
    # 10 Naval Roles
    roles = [
        "Optical Camera", "Thermal Sensor", "LIDAR", "Acoustic Sensor", "Manipulator Arm",
        "Payload Delivery", "Precision Navigation", "Electronic Scanner", "High-Endurance", "Defensive Module"
    ]
    
    for i in range(1, 11):
        cap = roles[i-1]
        a = Agent(i, cap, env)
        env.capabilities[i] = cap
        env.register(i)
        agents.append(a)

    # Formation Positions
    # 1 (Leader/Cam) at Top
    env.positions[1] = (25, 5)
    # Others spread out
    env.positions[2] = (15, 10); env.positions[3] = (35, 10)
    env.positions[4] = (10, 15); env.positions[5] = (20, 15); env.positions[6] = (30, 15); env.positions[7] = (40, 15)
    env.positions[8] = (15, 20); env.positions[9] = (25, 20); env.positions[10] = (35, 20)

    # Task (Needs LIDAR -> Agent 3)
    task = {
        "id": 101,
        "location": (35, 12), # Near Agent 3
        "capability": "LIDAR",
        "assigned_to": None,
        "completed": False,
        "locked": False
    }

    # Loop
    steps = 0
    phase = "INIT"
    
    # Track dead agents for the report
    graveyard = []
    
    # Next kill time (randomized between 20-40s from start)
    next_kill_time = 10.0 + random.randint(20, 40)

    try:
        while steps < 3000: # 300 seconds (5 mins) at 10Hz
            current_time = steps * 0.1
            
            # --- ATTRITION SCRIPT (KILL CHAIN) ---
            if current_time >= next_kill_time: 
                # Schedule NEXT kill (random 20-40s later)
                next_kill_time = current_time + random.randint(20, 40)
                
                leaders = [a for a in agents if a.role == Role.LEADER]
                if leaders:
                    victim = leaders[0]
                    # Kill it
                    agents.remove(victim)
                    graveyard.append(f"T={current_time:.1f}s: Killed Agent {victim.id} (Role: {victim.capability.upper()} LEADER)")
            
            # -------------------------------------

            # Logic Step
            for a in agents: a.step()
            env.tick()
            
            # Update Info for Draw
            active_leaders = [a.id for a in agents if a.role == Role.LEADER]
            display_term = 0
            if agents: display_term = agents[0].term

            # Draw
            clear_screen()
            draw_header(current_time, display_term)
            print(f"{RED}{BOLD}SCENARIO: ATTRITION WARFARE (KILLING LEADERS){RESET}")
            draw_map(agents, task)
            
            # Telemetry
            print(f"{BOLD}FLEET STATUS ({len(agents)} SURVIVORS):{RESET}")
            print(f"  Active Leaders: {active_leaders}")
            
            print(f"{BOLD}CASUALTY REPORT:{RESET}")
            for g in graveyard[-5:]: # Show last 5 deaths
                print(f"  {RED}† {g}{RESET}")
            
            if len(agents) == 1:
                print(f"{GREEN}{BOLD}!!! LAST STAND: AGENT {agents[0].id} IS THE FINAL COMMANDER !!!{RESET}")

            steps += 1
            time.sleep(0.05) # Speed up simulation slightly (2x speed)

    except KeyboardInterrupt:
        print("Simulation Stopped.")

if __name__ == "__main__":
    run_visual_demo()
