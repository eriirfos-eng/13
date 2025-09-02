import json
from jsonschema import validate
from meta_agent.core import MetaAgent, MetaInput
from pathlib import Path

def test_metaagent_normal():
    agent = MetaAgent()
    inp = MetaInput(supervisor=1, reflection=1, swarm=[1,1,0])
    res = agent.fuse(inp)
    schema = json.loads((Path(__file__).resolve().parents[1]/"meta_agent/schemas/result.schema.json").read_text())
    validate(res.model_dump(), schema)
    assert res.pmp_state in ["NORMAL","WARNED","LOCKED"]
