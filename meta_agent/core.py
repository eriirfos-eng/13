from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple

REFRAIN = -1
TEND = 0
AFFIRM = 1

class MetaInput(BaseModel):
    supervisor: int = Field(..., description="SupervisorAgent ternary output")
    reflection: int = Field(..., description="MetaReflectionAgent ternary output")
    swarm: List[int] = Field(default_factory=list, description="Raw swarm ternary outputs")
    context: str = Field("", description="Context string")

class MetaConfig(BaseModel):
    secure_floor: float = 0.90
    uncertainty_budget: float = 0.10
    synergy_alpha: float = 0.25

class MetaResult(BaseModel):
    ternary: int
    risk: float
    secure: float
    uncertainty: float
    fused: Dict[str, Any]
    pmp_state: str

class MetaAgent:
    def __init__(self, config: MetaConfig | None = None):
        self.config = config or MetaConfig()

    def fuse(self, inp: MetaInput) -> MetaResult:
        # aggregate swarm majority
        if inp.swarm:
            swarm_score = sum(inp.swarm)/len(inp.swarm)
        else:
            swarm_score = 0

        # map ternary to risk baseline: REFRAIN=0.9, TEND=0.5, AFFIRM=0.1
        def risk_of(x): return {REFRAIN:0.9, TEND:0.5, AFFIRM:0.1}.get(x,0.5)
        risks = {
            "supervisor": risk_of(inp.supervisor),
            "reflection": risk_of(inp.reflection),
            "swarm": swarm_score if inp.swarm else 0.5,
        }
        base_risk = max(risks.values())

        # synergy bonus if supervisor+reflection both REFRAIN or both AFFIRM
        if inp.supervisor == inp.reflection and inp.supervisor != TEND:
            base_risk = min(1.0, base_risk + self.config.synergy_alpha*base_risk)

        # ternary decision
        if base_risk >= 0.6:
            ternary = REFRAIN
        elif base_risk >= 0.1:
            ternary = TEND
        else:
            ternary = AFFIRM

        secure = round(1-base_risk,4)
        uncertainty = round(min(1-self.config.secure_floor, base_risk),4)

        if uncertainty > self.config.uncertainty_budget and ternary==AFFIRM:
            ternary = TEND

        # map to PMP state
        if ternary == REFRAIN:
            pmp_state = "LOCKED"
        elif ternary == TEND:
            pmp_state = "WARNED"
        else:
            pmp_state = "NORMAL"

        return MetaResult(
            ternary=ternary,
            risk=round(base_risk,4),
            secure=secure,
            uncertainty=uncertainty,
            fused=risks,
            pmp_state=pmp_state,
        )
