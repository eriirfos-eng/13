import argparse, json
from .core import MetaAgent, MetaInput

def main():
    p = argparse.ArgumentParser(prog="meta-agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run")
    run.add_argument("--context", type=str, default="")
    run.add_argument("--supervisor", type=int, required=True)
    run.add_argument("--reflection", type=int, required=True)
    run.add_argument("--swarm", type=int, nargs="*", default=[])

    def _run(args):
        agent = MetaAgent()
        inp = MetaInput(supervisor=args.supervisor, reflection=args.reflection,
                        swarm=args.swarm, context=args.context)
        res = agent.fuse(inp)
        print(json.dumps(res.model_dump(), indent=2))

    run.set_defaults(func=_run)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
