class IncidentEnv:
    def __init__(self):
        self.state = None
        self.done = False
        self.history = []

    # 🔥 Initialize from USER INPUT (NO DEFAULT)
    def initialize(self, user_input: dict):
        required_fields = ["issue", "cpu", "battery", "context", "apps_running"]

        for field in required_fields:
            if field not in user_input:
                raise ValueError(f"Missing field: {field}")

        self.state = {
            "issue": user_input["issue"],
            "cpu": user_input["cpu"],
            "battery": user_input["battery"],
            "context": user_input["context"],
            "apps_running": user_input["apps_running"]
        }

        self.done = False
        self.history = []

        return self.state

    # 🔥 Step function (UPGRADED)
    def step(self, action: dict):
        if self.state is None:
            raise ValueError("Environment not initialized")

        if self.done:
            return self.state, 0.0, True, {}

        action_type = action.get("action_type", "")
        prev_cpu = self.state.get("cpu", 50)
        reward = 0.0

        self.history.append(action_type)

        # 🎯 ACTION EFFECTS
        if action_type == "close_apps":
            if self.state["apps_running"] > 5:
                self.state["apps_running"] -= 5
                self.state["cpu"] -= 15
                reward += 0.5
            else:
                reward -= 0.2

        elif action_type == "optimize_cpu":
            self.state["cpu"] -= 10
            reward += 0.4

        elif action_type == "clear_cache":
            self.state["cpu"] -= 5
            reward += 0.2

        elif action_type == "reduce_brightness":
            if self.state["battery"] < 20:
                self.state["cpu"] -= 3
                reward += 0.3
            else:
                reward += 0.1

        elif action_type == "restart_device":
            if self.state["context"] == "user_call":
                reward -= 1.0  # ❌ bad decision
            else:
                self.state["cpu"] = 25
                reward += 0.6

        else:
            reward -= 0.5  # invalid action

        # ✅ LIMIT VALUES
        self.state["cpu"] = max(0, min(100, self.state["cpu"]))
        self.state["apps_running"] = max(0, self.state["apps_running"])

        new_cpu = self.state["cpu"]

        # 🚀 ADVANCED REWARD SHAPING (MAIN FIX)
        improvement = prev_cpu - new_cpu

        if improvement > 15:
            reward += 1.0
        elif improvement > 5:
            reward += 0.5
        elif improvement > 0:
            reward += 0.2
        else:
            reward -= 0.3

        # ✅ Stability bonus
        if new_cpu < 50:
            reward += 0.3

        # 🎯 SUCCESS CONDITION
        if new_cpu < 40 and self.state["apps_running"] <= 3:
            reward += 1.0
            self.done = True

        return self.state, round(reward, 3), self.done, {}

    def get_state(self):
        return self.state