import os
import time
import random
import logging
import gradio as gr
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ================= CONFIG =================
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
BASE_URL = os.getenv("BASE_URL", "https://nirfan206-alphamatrix.hf.space").rstrip("/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaMatrix")

session = requests.Session()

cpu_history = []
reward_history = []
actions_log = []

ACTIONS = [
    "close_apps","clear_cache","reduce_brightness",
    "restart_device","free_storage","optimize_cpu"
]

# ================= API =================
def safe_get(url):
    try:
        res = session.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except:
        return {}

def safe_post(url, data):
    try:
        res = session.post(url, json=data, timeout=10)
        res.raise_for_status()
        return res.json()
    except:
        return {}

def check_backend():
    res = safe_get(f"{BASE_URL}/health")
    return "🟢 Backend Connected" if res else "❌ Backend Offline"

# ================= PLOT =================
def build_plot(data, title, color):
    fig, ax = plt.subplots(figsize=(6,3))
    if data:
        x = list(range(len(data)))
        ax.plot(x, data, marker="o", linewidth=2, color=color)
        ax.fill_between(x, data, color=color, alpha=0.2)
    ax.set_title(title)
    ax.grid(True)
    return fig

# ================= INIT =================
def initialize(issue, cpu, battery, context, apps):
    res = safe_post(f"{BASE_URL}/initialize", {
        "issue": issue,
        "cpu": int(cpu),
        "battery": int(battery),
        "context": context,
        "apps": int(apps)
    })

    if not res or "state" not in res:
        return {}, "❌ Initialization Failed", "Check backend logs", build_plot([], "CPU","#ef4444"), build_plot([], "Reward","#22c55e")

    state = res["state"]

    cpu_history.clear()
    reward_history.clear()
    actions_log.clear()

    cpu_history.append(state.get("cpu",0))

    return state, "🟢 Initialized Successfully", "System Ready", build_plot(cpu_history,"CPU","#ef4444"), build_plot([], "Reward","#22c55e")

# ================= STEP =================
def step(action):
    res = safe_post(f"{BASE_URL}/step", {"action_type": action})

    if not res or "observation" not in res:
        return {}, "❌ Backend Error", build_plot([], "CPU","#ef4444"), build_plot([], "Reward","#22c55e"), "Error", "", ""

    obs = res["observation"]
    reward = res.get("reward",0)

    cpu = obs.get("cpu",0)
    cpu_history.append(cpu)
    reward_history.append(reward)

    explain = safe_get(f"{BASE_URL}/explain")
    predict = safe_get(f"{BASE_URL}/predict")
    metrics = safe_get(f"{BASE_URL}/metrics")
    status_data = safe_get(f"{BASE_URL}/status")

    level = status_data.get("status","stable")

    logs = f"{action} → CPU {cpu:.2f} | Reward {reward:.2f}"

    cpu_fig = build_plot(cpu_history,"CPU Trend","#ef4444")
    reward_fig = build_plot(reward_history,"Reward Trend","#22c55e")

    ai_panel = f"""
### 🤖 AI Decision
Reason: {explain.get("explanation","-")}
Prediction: {predict.get("predicted_action","-")}
Confidence: {predict.get("confidence","-")}
Status: {level.upper()}
"""

    metrics_panel = f"""
### 📊 Metrics
Steps: {metrics.get("steps","-")}
Avg Reward: {metrics.get("avg_reward","-")}
"""

    return obs, f"⚡ Reward: {reward}", cpu_fig, reward_fig, logs, ai_panel, metrics_panel

# ================= AUTO =================
def auto_run():
    for _ in range(5):
        yield step(random.choice(ACTIONS))
        time.sleep(1)

# ================= CSS =================
css = """
body {background:#020617;color:white;font-family:sans-serif;}
.card {
background:rgba(255,255,255,0.05);
padding:15px;border-radius:12px;
backdrop-filter:blur(10px);
box-shadow:0 0 20px rgba(0,0,0,0.5);
margin-bottom:10px;
}
button {
background:linear-gradient(90deg,#3b82f6,#9333ea);
color:white;border:none;border-radius:8px;
transition:0.3s;
}
button:hover {
transform:scale(1.05);
box-shadow:0 0 10px #9333ea;
}
"""

# ================= UI =================
with gr.Blocks(css=css) as demo:

    gr.Markdown("# 🚀 AlphaMatrix AI System")

    with gr.Row():
        backend = gr.Markdown(check_backend())
        gr.Button("Refresh").click(check_backend, outputs=backend)

    with gr.Column(elem_classes="card"):
        issue = gr.Textbox(value="overheating", label="Issue")
        cpu = gr.Number(value=90,label="CPU")
        battery = gr.Number(value=10,label="Battery")
        context = gr.Textbox(value="user_call",label="Context")
        apps = gr.Number(value=15,label="Apps")

        init_btn = gr.Button("Initialize")

    state = gr.JSON()
    status = gr.Markdown()
    logs = gr.Textbox()

    with gr.Row():
        cpu_chart = gr.Plot()
        reward_chart = gr.Plot()

    init_btn.click(initialize,
                   [issue,cpu,battery,context,apps],
                   [state,status,logs,cpu_chart,reward_chart])

    with gr.Column(elem_classes="card"):
        action = gr.Dropdown(ACTIONS,value="close_apps")
        step_btn = gr.Button("Run Step")
        auto_btn = gr.Button("Auto Mode")

    reward = gr.Markdown()
    ai = gr.Markdown()
    metrics = gr.Markdown()

    step_btn.click(step,action,
                   [state,reward,cpu_chart,reward_chart,logs,ai,metrics])

    auto_btn.click(auto_run,
                   outputs=[state,reward,cpu_chart,reward_chart,logs,ai,metrics])

# ================= RUN =================
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)