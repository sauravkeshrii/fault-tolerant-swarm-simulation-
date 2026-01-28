from agent import Agent
from test_env import LossyEnv

env = LossyEnv(drop_prob=0.3)

agents = [
    Agent(1, "camera", env),
    Agent(2, "camera", env),
    Agent(3, "lidar", env),
]

for a in agents:
    env.register(a.id)

# inject task
env.send({
    "type": "TASK_NEW",
    "task": {
        "id": 1,
        "location": (4, 4),
        "capability": "camera",
        "deadline": 50.0
    }
})

for _ in range(500):
    for a in agents:
        a.step()
    env.tick()
