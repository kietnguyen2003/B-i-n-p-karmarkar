"""[MasterSpec C11-C12,8; DX] Real benchmark CLI, reference isolated from core."""
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
from karmarkar.io import load_config
from karmarkar.experiments import dataset_cases,run_benchmark
from karmarkar.plotting import plot_benchmark,save_figure,set_style


def main():
    """[MS G6] Retain every run and produce CSV/JSON/figures/environment manifest."""
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,default=root/"configs/default.yaml")
    args=parser.parse_args()
    config,raw=load_config(args.config)
    data,summary=run_benchmark(dataset_cases(raw["seed"]),config,raw["repetitions"],raw["seed"],root/"outputs")
    set_style()
    for name,fig in plot_benchmark(data,summary).items():
        save_figure(fig,root/"outputs/figures",name)
        plt.close(fig)
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()

