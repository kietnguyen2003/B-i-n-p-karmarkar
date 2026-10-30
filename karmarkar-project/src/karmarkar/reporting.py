"""[MS C10-C12, NB01-NB68; BC 4.1-4.5] Notebook displays and reproducible evidence."""
from dataclasses import asdict
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from . import plotting as plots
from .types import SolverConfig
from .solver import solve_karmarkar
from .examples import report_example_lp, u_to_original
from .potential import potential
from .io import plain, write_json


def show_step_table(step, include_matrices: bool = True) -> pd.DataFrame:
    """[MS NB31-NB34, NB44-NB48; BC (4.37)-(4.41)] Display actual step, bounded matrix size."""
    rows=[]
    for key in ("k","x_before","D","B","v","p","d","y","x_after","f_before","f_after","phi_before","phi_after","status"):
        value=getattr(step,key)
        if isinstance(value,np.ndarray):
            if value.ndim==2 and (not include_matrices or max(value.shape,default=0)>8):
                value={"shape":value.shape,"norm":float(np.linalg.norm(value)),"preview_5x5":value[:5,:5].tolist()}
            else:
                value=np.array2string(value,precision=9,suppress_small=False)
        rows.append({"Đại lượng":key,"Giá trị":value})
    rows.extend({"Đại lượng":k,"Giá trị":plain(v)} for k,v in step.diagnostics.items() if k!="singular_values")
    return pd.DataFrame(rows)


def example_history(result) -> pd.DataFrame:
    """[BC Table 4.2; MS 7.2] Build history exclusively from actual solver data."""
    k,points=plots.trace_arrays(result)
    c=report_example_lp().c
    return pd.DataFrame([{"k":int(i),"x1":float(2*u[0]),"x2":float(2*u[1]),
                          "w":float(c@u),"z":float(2*c@u),"phi":potential(u,c),
                          "min_u":float(u.min()),"eq_residual":0.,
                          "sum_residual":float(abs(u.sum()-1))} for i,u in zip(k,points)])


def methods_table() -> pd.DataFrame:
    """[BC Table 4.3,4.4.11] Preserve source comparison, no invented timing numbers."""
    return pd.DataFrame({"criterion":["Bài toán xét","Cách giải","Kết quả","Phạm vi"],
        "geometry_method":["Hai biến, miền tam giác OAB","Vẽ miền chấp nhận được; so sánh mục tiêu tại các đỉnh",
                           "(x1*,x2*)=(2,0), z*=0","Thuận lợi khi có hai biến"],
        "karmarkar_method":["Cùng bài toán, sau khi thêm biến bù và chuẩn hóa",
                            "Tạo dãy điểm trong bằng phép chiếu và biến đổi xạ ảnh",
                            "(x1(k),x2(k))→(2,0), z(k)→0","Áp dụng cho bài toán nhiều biến ở dạng chuẩn"]})


def export_example_artifacts(output_dir: Path, config: SolverConfig | None = None):
    """[MS C12,7.1-7.2; BC 4.1-4.4] Run source example; regenerate 8 figures, 3 tables, trace.

    INPUT: portable output directory, validated configuration. OUTPUT: actual
    SolverResult plus history. Source table requires at least 20 completed steps.
    """
    out=Path(output_dir)
    config=config or SolverConfig()
    result=solve_karmarkar(report_example_lp(),config)
    history=example_history(result)
    if len(history)<=20:
        raise ValueError("source artifact export needs >=20 steps; use a smaller canonical epsilon or a larger iteration budget")
    (out/"tables").mkdir(parents=True,exist_ok=True)
    vertices=pd.DataFrame({"vertex":["O","A","B"],"x1":[0,2,0],"x2":[0,0,2]})
    vertices["z"]=2-vertices.x1
    vertices.to_csv(out/"tables/table_4_1_vertices.csv",index=False,encoding="utf-8-sig")
    history[history.k.isin([0,1,2,3,10,20])].to_csv(out/"tables/table_4_2_iterations.csv",index=False,encoding="utf-8-sig")
    methods_table().to_csv(out/"tables/table_4_3_methods.csv",index=False,encoding="utf-8-sig")
    history.to_csv(out/"tables/source_full_history.csv",index=False,encoding="utf-8-sig")
    monitor=history[["k","w","z","phi","min_u","eq_residual","sum_residual"]].copy()
    monitor["delta_phi"]=monitor.phi.diff()
    monitor["decrease_threshold"]=1/8
    monitor["scope_status"]=result.diagnostics["theorem_scope"]
    monitor.to_csv(out/"tables/potential_history.csv",index=False,encoding="utf-8-sig")
    diagnostic_rows=[]
    for s in result.trace:
        diagnostic_rows.append({"k":s.k,"x_before":plain(s.x_before),"x_after":plain(s.x_after),
                                "phi_before":s.phi_before,"phi_after":s.phi_after,"status":s.status,
                                **{k:v for k,v in s.diagnostics.items() if np.isscalar(v) or v is None}})
    pd.DataFrame(diagnostic_rows).to_csv(out/"tables/step_diagnostics.csv",index=False,encoding="utf-8-sig")
    write_json(out/"traces/source_example.json",result)
    plots.set_style()
    factories=[plots.plot_figure_4_1,plots.plot_figure_4_2,plots.plot_figure_4_3,
               plots.plot_figure_4_4,plots.plot_figure_4_5,
               lambda: plots.plot_figure_4_6(result.trace[0]),plots.plot_figure_4_7,
               lambda: plots.plot_figure_4_8(result)]
    for i,make in enumerate(factories,1):
        fig=make()
        plots.save_figure(fig,out/"figures",f"figure_4_{i}")
        plt.close(fig)
    fig=plots.plot_original_geometry()
    plots.save_figure(fig,out/"figures","geometry_4_4_2")
    plt.close(fig)
    for name,fig in plots.plot_histories(result).items():
        plots.save_figure(fig,out/"figures",name)
        plt.close(fig)
    return result,history


def audit_project(root: Path, require_executed: bool = False) -> dict:
    """[MS NB67,11.1-11.3] Audit source IDs, 68 annotated cells and actual artifact files."""
    import nbformat
    root=Path(root)
    notebook=root/"notebooks/01_karmarkar_full_report.ipynb"
    if require_executed:
        notebook=notebook.with_name("01_karmarkar_full_report_executed.ipynb")
    nb=nbformat.read(notebook,as_version=4)
    expected=[f"NB{i:02}" for i in range(1,69)]
    found=[]
    execution=[]
    four=("Đang làm gì","Vì sao cần","Input/Output","Cần nhìn kết quả nào")
    for i,cell in enumerate(nb.cells):
        if cell.cell_type!="code":
            continue
        ids=re.findall(r"^# (NB\d\d)\b",cell.source,re.M)
        found.extend(ids)
        assert i>0 and all(label in nb.cells[i-1].source for label in four),f"missing preface: {ids}"
        assert i+1<len(nb.cells) and nb.cells[i+1].cell_type=="markdown",f"missing interpretation: {ids}"
        assert "MasterSpec" in cell.source and "BC" in cell.source,f"missing source annotation: {ids}"
        if require_executed:
            assert cell.execution_count is not None,f"unexecuted: {ids}"
            assert not any(o.output_type=="error" for o in cell.outputs),f"error: {ids}"
            execution.append(cell.execution_count)
    assert found==expected,"missing or reordered notebook IDs"
    mapping=(root/"docs/mapping_report_sections.md").read_text(encoding="utf-8")
    sections=[f"4.{major}.{minor}" for major,count in [(1,3),(2,8),(3,5),(4,11),(5,3)] for minor in range(1,count+1)]
    assert all(s in mapping for s in sections)
    artifacts=[root/"outputs/figures"/f"figure_4_{i}.{ext}" for i in range(1,9) for ext in ("png","svg")]
    artifacts += [root/"outputs/tables"/s for s in ["table_4_1_vertices.csv","table_4_2_iterations.csv","table_4_3_methods.csv","benchmark_results.csv"]]
    assert all(p.is_file() and p.stat().st_size>0 for p in artifacts),"artifact missing/empty"
    return {"notebook_ids":len(found),"source_subsections":len(sections),"artifacts_checked":len(artifacts),
            "executed":require_executed,"execution_counts":execution,"status":"PASS"}

