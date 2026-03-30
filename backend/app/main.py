from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.env import IncidentEnv
from app.grader import Grader

app = FastAPI()

env = IncidentEnv()
grader = Grader()

history = []
reward_history = []
action_history = []
context_memory = []


# 🟢 HEALTH
@app.get("/health")
def health():
    return {"status": "healthy"}


# 🔥 INITIALIZE (FINAL FIX)
@app.post("/initialize")
def initialize(data: dict):
    try:
        print("🔥 INIT DATA:", data)

        # ✅ FIX: SUPPORT BOTH KEYS
        apps_running = data.get("apps_running") or data.get("apps", 5)

        safe_data = {
            "issue": data.get("issue", "unknown"),
            "cpu": int(data.get("cpu", 50)),
            "battery": int(data.get("battery", 50)),
            "context": data.get("context", "normal"),
            "apps_running": int(apps_running),
        }

        # 🚀 INIT ENV
        state = env.initialize(safe_data)

        # ✅ SAFETY (VERY IMPORTANT)
        if state is None:
            state = safe_data  # fallback

        print("✅ STATE:", state)

        # RESET MEMORY
        history.clear()
        reward_history.clear()
        action_history.clear()
        context_memory.clear()

        return {"status": "success", "state": state}

    except Exception as e:
        print("❌ INIT ERROR:", str(e))

        # 🔥 NEVER FAIL HARD — RETURN SAFE STATE
        return {
            "status": "fallback",
            "state": {
                "cpu": data.get("cpu", 50),
                "battery": data.get("battery", 50),
                "apps_running": data.get("apps", 5)
            }
        }


# ⚡ STEP
@app.post("/step")
def step(action: dict):
    try:
        print("⚡ STEP INPUT:", action)

        action_type = action.get("action_type") or action.get("action")

        if not action_type:
            raise ValueError("Missing action_type")

        # ❗ CHECK INIT
        current_state = env.get_state()
        if current_state is None:
            raise ValueError("Environment not initialized")

        prev_cpu = current_state.get("cpu", 0)

        state, reward, done, info = env.step({"action_type": action_type})

        if state is None:
            raise ValueError("Env returned None state")

        cpu = state.get("cpu", 0)

        history.append(state)
        reward_history.append(reward)
        action_history.append(action_type)

        context_memory.append({
            "cpu": cpu,
            "action": action_type,
            "reward": reward
        })

        # 🤖 AI LOGIC
        if cpu > 85:
            reason = "Critical CPU overload"
            next_action = "close_apps"
        elif cpu > 70:
            reason = "Moderate CPU load"
            next_action = "optimize_cpu"
        else:
            reason = "System stable"
            next_action = "clear_cache"

        improvement = prev_cpu - cpu
        improvement_pct = (improvement / prev_cpu * 100) if prev_cpu else 0

        return {
            "status": "success",
            "observation": state,
            "reward": reward,
            "reason": reason,
            "impact": {
                "cpu_before": prev_cpu,
                "cpu_after": cpu,
                "improvement_percent": round(improvement_pct, 2)
            },
            "suggested_action": next_action
        }

    except Exception as e:
        print("❌ STEP ERROR:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=400)


# 📊 STATUS
@app.get("/status")
def system_status():
    state = env.get_state() or {}
    cpu = state.get("cpu", 0)

    if cpu > 85:
        level = "critical"
    elif cpu > 70:
        level = "warning"
    else:
        level = "stable"

    return {"cpu": cpu, "status": level}


# 🧠 EXPLAIN
@app.get("/explain")
def explain():
    if not context_memory:
        return {"explanation": "No actions yet"}

    last = context_memory[-1]

    return {
        "last_action": last["action"],
        "cpu": last["cpu"],
        "reward": last["reward"],
        "explanation": "AI selects actions based on CPU trends"
    }


# 🔮 PREDICT
@app.get("/predict")
def predict():
    if not context_memory:
        return {"predicted_action": "close_apps", "confidence": 0.5}

    cpus = [x["cpu"] for x in context_memory[-5:]]
    avg_cpu = sum(cpus) / len(cpus)

    if avg_cpu > 85:
        action = "close_apps"
    elif avg_cpu > 70:
        action = "optimize_cpu"
    else:
        action = "clear_cache"

    return {
        "predicted_action": action,
        "confidence": round(avg_cpu / 100, 2)
    }


# 📊 METRICS
@app.get("/metrics")
def metrics():
    if not reward_history:
        return {"steps": 0, "avg_reward": 0}

    avg_reward = sum(reward_history) / len(reward_history)

    return {
        "steps": len(reward_history),
        "avg_reward": round(avg_reward, 3)
    }