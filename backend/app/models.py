from pydantic import BaseModel

class Action(BaseModel):
    action_type: str

class Observation(BaseModel):
    issue: str
    cpu: int
    battery: int
    context: str
    apps_running: int

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict