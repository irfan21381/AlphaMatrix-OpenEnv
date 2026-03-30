class Grader:
    def __init__(self):
        pass

    def evaluate(self, history, final_state):
        score = 0.0

        # ✅ Action intelligence
        if "close_apps" in history:
            score += 0.3

        if "optimize_cpu" in history:
            score += 0.2

        # ✅ Efficiency (fewer steps better)
        if len(history) <= 3:
            score += 0.3
        elif len(history) <= 6:
            score += 0.2
        else:
            score -= 0.1

        # ✅ Final system condition
        if final_state["cpu"] < 50:
            score += 0.2

        if final_state["apps_running"] <= 5:
            score += 0.1

        # Normalize
        return max(0.0, min(1.0, round(score, 3)))