import random
import time

class LossyEnv:
    def __init__(self, drop_prob=0.3):
        self.drop_prob = drop_prob
        self.inboxes = {} # robot_id -> list of msgs
        self.time = 0.0
        self.positions = {}
        self.capabilities = {}

    def register(self, robot_id):
        self.inboxes[robot_id] = []

    # -------- simulator-like APIs --------
    def send(self, msg):
        # Broadcast to all registered inboxes
        if random.random() > self.drop_prob:
            for rid in self.inboxes:
                # Deep copy or JSON dump/load would be better, but ref copy is ok here
                self.inboxes[rid].append(msg)

    def receive(self, robot_id):
        if robot_id not in self.inboxes:
            return []
        msgs = self.inboxes[robot_id][:]
        self.inboxes[robot_id].clear()
        return msgs

    def get_time(self):
        return self.time

    def tick(self, dt=0.1):
        self.time += dt

    def get_position(self, robot_id):
        return self.positions.get(robot_id, (0.0, 0.0))

    def get_neighbors(self):
        return list(self.positions.keys())

    def has_capability(self, robot_id, capability):
        return self.capabilities.get(robot_id) == capability
