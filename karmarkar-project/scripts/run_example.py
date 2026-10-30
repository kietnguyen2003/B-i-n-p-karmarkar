"""[MasterSpec C09-C12; BC 4.4.1-4.4.11] CLI to regenerate source figures/tables."""
from pathlib import Path
import argparse
from dataclasses import replace
from karmarkar.io import load_config
from karmarkar.reporting import export_example_artifacts


def main():
    """[MS G4-G5] epsilon is CANONICAL w, while reported z is 2w."""
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description="BC 4.4: source example (epsilon applies to w=z/2)")
    parser.add_argument("--alpha",type=float)
    parser.add_argument("--epsilon",type=float)
    args=parser.parse_args()
    config,_=load_config(root/"configs/default.yaml")
    changes={k:v for k,v in vars(args).items() if v is not None}
    result,history=export_example_artifacts(root/"outputs",replace(config,**changes))
    print(f"status={result.status.value}; iterations={result.iterations}; w={result.objective:.10g}; z={2*result.objective:.10g}")
    print(f"actual history rows={len(history)}; outputs={root/'outputs'}")


if __name__=="__main__":
    main()

