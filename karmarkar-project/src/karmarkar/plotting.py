"""[MS C10/M10, 7.1; BC Figures 4.1-4.8] Rebuilt figures from definitions/traces."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
from .geometry import simplex_geometry, simplex_embedding
from .projective import to_projective
from .examples import u_to_original

PALETTE = {"feasible":"#dceef7","current":"#174a73","next":"#d34a35",
           "ball":"#2675bf","direction":"#087f78","warning":"#b26200"}


def set_style() -> dict:
    """[MS NB04, 5.1] One readable Vietnamese palette and font across outputs."""
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
                         "axes.titlesize":12,"figure.dpi":110,"savefig.dpi":180})
    return PALETTE.copy()


def save_figure(fig, directory: Path, stem: str) -> list[Path]:
    """[MS 7.1] Export both PNG and editable SVG, with stable filenames."""
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    paths=[]
    for ext in ("png","svg"):
        p=directory/f"{stem}.{ext}"
        fig.savefig(p,bbox_inches="tight",facecolor="white")
        paths.append(p)
    return paths


def _triangle(ax, title: str):
    """[BC 4.1.1,4.4.2] Original feasible OAB triangle in (x1,x2)."""
    ax.add_patch(Polygon([[0,0],[2,0],[0,2]],facecolor=PALETTE["feasible"],edgecolor="#233c50"))
    for xy,label,offset in [((0,0),"O",(-.12,-.13)),((2,0),"A=(2,0)",(-.35,-.16)),((0,2),"B=(0,2)",(.04,.03))]:
        ax.plot(*xy,"o",color="#233c50",ms=4)
        ax.text(xy[0]+offset[0],xy[1]+offset[1],label,fontsize=9)
    ax.set(xlim=(-.25,2.35),ylim=(-.25,2.35),xlabel="$x_1$",ylabel="$x_2$",title=title)
    ax.set_aspect("equal")
    ax.grid(alpha=.18)


def _simplex(ax,title: str):
    """[BC 4.2.2; MS Fig 4.3] Use an isometric embedding of all three vertices."""
    v=simplex_embedding(np.eye(3))
    ax.add_patch(Polygon(v,facecolor=PALETTE["feasible"],edgecolor="#233c50"))
    for xy,label in zip(v,("$e_1$","$e_2$","$e_3$")):
        ax.plot(*xy,"ko",ms=3)
        ax.annotate(label,xy,xytext=(5,5),textcoords="offset points")
    ax.set(xlim=(-.95,.95),ylim=(-1,.95),title=title)
    ax.set_aspect("equal")
    ax.axis("off")


def plot_figure_4_1(problem=None,levels=(0.6,1.4)):
    """[BC 4.1.1, Fig 4.1, (4.1)] Halfplanes, objective levels and -gradient."""
    fig,ax=plt.subplots(figsize=(6.5,5))
    _triangle(ax,"Hình 4.1 • Miền chấp nhận được và đường mức")
    for z in levels:
        ax.axvline(2-z,color=PALETTE["next"],ls="--",lw=1)
        ax.text(2-z+.03,1.85,f"z={z:g}",rotation=90,color=PALETTE["next"])
    ax.annotate("",xy=(1.3,.65),xytext=(.55,.65),arrowprops={"arrowstyle":"->","color":PALETTE["direction"],"lw":2})
    ax.text(.7,.46,r"$-\nabla z=(1,0)$",color=PALETTE["direction"])
    fig.text(.1,.01,"Tái dựng theo Hình 4.1 • z=2−x₁; miền là giao ba nửa mặt phẳng.",fontsize=9)
    return fig


def plot_figure_4_2():
    """[BC 4.1.2, Fig 4.2, (4.44)] Slack/linear normalization, distinct from xạ ảnh."""
    fig,axs=plt.subplots(1,2,figsize=(11,4.5))
    _triangle(axs[0],"Tọa độ gốc $(x_1,x_2)$")
    _simplex(axs[1],"Tọa độ chuẩn $(u_1,u_2,u_3)$")
    axs[0].plot(2/3,2/3,"o",color=PALETTE["next"])
    axs[1].plot(0,0,"o",color=PALETTE["next"])
    axs[1].text(.05,-.1,"$a_0=e/3$")
    fig.suptitle("Hình 4.2 • Cùng miền qua hai cách biểu diễn")
    fig.text(.15,.01,"u₁=x₁/2; u₂=x₂/2; u₃=(2−x₁−x₂)/2.   O↔e₃; A↔e₁; B↔e₂.",fontsize=10)
    fig.subplots_adjust(top=.83,bottom=.13,wspace=.25)
    return fig


def plot_figure_4_3():
    """[BC 4.2.2, Fig 4.3, (4.11)] Accurate Euclidean in/circumcircles."""
    fig,ax=plt.subplots(figsize=(6,5.3))
    _simplex(ax,"Hình 4.3 • Hai quả cầu đồng tâm (thiết diện 2D)")
    _,r,R=simplex_geometry(3)
    ax.add_patch(Circle((0,0),R,fill=False,color="#cf8421",ls="--",label="$R=\\sqrt{2/3}$"))
    ax.add_patch(Circle((0,0),r,fill=False,color=PALETTE["ball"],lw=2,label="$r=1/\\sqrt{6}$"))
    ax.plot(0,0,"ko",ms=4)
    ax.text(.03,.03,"$a_0$")
    ax.plot([0,r],[0,0],color=PALETTE["ball"])
    ax.legend(loc="upper right",fontsize=9)
    fig.text(.1,.015,"Tái dựng theo Hình 4.3 • Embedding trực chuẩn, giữ độ dài; R/r=2.",fontsize=9)
    return fig


def plot_figure_4_4():
    """[BC 4.2.3, Fig 4.4] Explicitly schematic 2D orthogonal projection."""
    fig,ax=plt.subplots(figsize=(7,4))
    ax.axhline(0,color="#566a78",lw=2)
    vectors=[((1.7,1.2),"$v$",PALETTE["next"]),((1.7,0),"$p$",PALETTE["ball"]),((-1.3,0),"$-p$",PALETTE["direction"])]
    for end,label,color in vectors:
        ax.annotate("",end,(0,0),arrowprops={"arrowstyle":"->","lw":2,"color":color})
        ax.text(end[0]+.05,end[1]+.05,label,color=color)
    ax.plot([1.7,1.7],[0,1.2],"k--")
    ax.plot([1.55,1.55,1.7],[0,.15,.15],"k-",lw=1)
    ax.text(1.8,.6,"$v-p$",fontsize=11)
    ax.text(-1.8,-.3,r"$\mathrm{Ker}\,B$")
    ax.set(xlim=(-2.1,2.7),ylim=(-.5,1.7),title="Hình 4.4 • Phép chiếu trực giao (minh họa 2D)")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(.12,.02,"Tái dựng theo Hình 4.4 • p∈Ker B; v−p vuông góc không gian hướng.",fontsize=9)
    return fig


def plot_figure_4_5(a=None,other_points=None):
    """[BC 4.2.4, Fig 4.5] A single fixed a maps all displayed sample points."""
    a=np.array([.5,.25,.25]) if a is None else np.asarray(a)
    b=np.array([2/3,1/6,1/6])
    points=np.array([[i/8,j/8,1-(i+j)/8] for i in range(1,7) for j in range(1,8-i)])
    if other_points is not None:
        points=np.asarray(other_points)
    fig,axs=plt.subplots(1,2,figsize=(10,4.7))
    for ax,title in zip(axs,("Hệ tọa độ x", "Hệ tọa độ y=Tₐ(x)")):
        _simplex(ax,title)
    for ax,pts in zip(axs,(points,np.array([to_projective(a,x) for x in points]))):
        xy=simplex_embedding(pts)
        ax.scatter(xy[:,0],xy[:,1],s=10,color="#839fb5",alpha=.6)
    for ax,aa,bb in ((axs[0],a,b),(axs[1],to_projective(a,a),to_projective(a,b))):
        for point,label,color in ((aa,"a" if ax is axs[0] else "Tₐ(a)=a₀",PALETTE["next"]),
                                  (bb,"b" if ax is axs[0] else "Tₐ(b)",PALETTE["direction"])):
            xy=simplex_embedding(point)
            ax.plot(*xy,"o",color=color)
            ax.annotate(label,xy,xytext=(5,-14),textcoords="offset points",color=color)
    fig.suptitle("Hình 4.5 • Xạ ảnh theo cùng một mốc a=(1/2,1/4,1/4)")
    fig.text(.12,.02,"Tái dựng theo Hình 4.5 • Tₐ(b)=(1/2,1/4,1/4), khác trọng tâm.",fontsize=9)
    fig.subplots_adjust(top=.84)
    return fig


def plot_figure_4_6(step_record):
    """[BC 4.2.5, Fig 4.6, (4.27)] Actual transformed step inside the inscribed ball."""
    fig,ax=plt.subplots(figsize=(6.5,5))
    _,r,_=simplex_geometry(3)
    y=simplex_embedding(step_record.y)
    direction=y/np.linalg.norm(y)
    ax.add_patch(Circle((0,0),r,color=PALETTE["ball"],fill=False,lw=2,label="Bán kính r"))
    ax.add_patch(Circle((0,0),np.linalg.norm(y),color=PALETTE["direction"],fill=False,ls="--",label="Bán kính αr"))
    ax.plot(0,0,"ko",ms=4)
    ax.text(-.07,.025,"$a_0$")
    ax.annotate("",y,(0,0),arrowprops={"arrowstyle":"->","lw":2,"color":PALETTE["next"]})
    ax.plot(*y,"o",color=PALETTE["next"])
    ax.annotate("$y^+$",y,xytext=(5,-15),textcoords="offset points")
    ax.annotate("",-.65*r*direction,(0,0),arrowprops={"arrowstyle":"->","color":"#cc8200"})
    ax.text(*(-.8*r*direction),"$p/\\|p\\|$",color="#a46800")
    ax.set(xlim=(-.5,.5),ylim=(-.5,.5),title="Hình 4.6 • Bước theo hướng −p, độ dài αr")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper right")
    fig.text(.1,.02,"Tái dựng theo Hình 4.6 • Mặt phẳng đẳng cự; α=1/4, αr<r.",fontsize=9)
    return fig


def plot_figure_4_7():
    """[BC 4.3.4, Fig 4.7; Algorithm 4.1] Six stages with explicit loop."""
    fig,ax=plt.subplots(figsize=(11,4.7))
    positions=[(.04,.62),(.37,.62),(.7,.62),(.7,.18),(.37,.18),(.04,.18)]
    labels=["1. Điểm hiện tại x⁽ᵏ⁾\nKiểm tra khả thi, dương", "2. Đưa về trọng tâm\nD=diag(x); B=[AD;eᵀ]",
            "3. Chiếu và chuẩn hóa\np=Π(Dc); d=−p/‖p‖", "4. Bước trong quả cầu\ny=a₀+αrd",
            "5. Xạ ảnh ngược\nx⁽ᵏ⁺¹⁾=Dy/(eᵀDy)","6. Đánh giá / dừng\nMục tiêu, Φ, residuals"]
    w,h=.25,.2
    for (x,y),label in zip(positions,labels):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012",facecolor="#edf4fa",edgecolor=PALETTE["current"]))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=9)
    edges=[((.29,.72),(.37,.72)),((.62,.72),(.7,.72)),((.825,.62),(.825,.38)),
           ((.7,.28),(.62,.28)),((.37,.28),(.29,.28)),((.165,.38),(.165,.62))]
    for start,end in edges:
        ax.annotate("",end,start,arrowprops={"arrowstyle":"->","color":PALETTE["direction"],"lw":1.7})
    ax.text(.04,.46,"Tiếp tục",fontsize=8,color=PALETTE["direction"])
    ax.set(xlim=(0,1),ylim=(0,1),title="Hình 4.7 • Một vòng lặp Karmarkar")
    ax.axis("off")
    fig.text(.1,.01,"Tái dựng theo Hình 4.7 • Theo dõi cả hệ chuẩn ban đầu và hệ xạ ảnh.",fontsize=9)
    return fig


def trace_arrays(result) -> tuple[np.ndarray,np.ndarray]:
    """[BC 4.4.9; MS NB50, Fig 4.8] Extract only ACTUAL solver iterates."""
    if result.trace:
        points=[result.trace[0].x_before]+[s.x_after for s in result.trace if s.x_after is not None and s.status is None]
    else:
        points=[result.x]
    return np.arange(len(points)),np.array(points)


def plot_figure_4_8(trace):
    """[BC 4.4.9, Fig 4.8] Real trace, k=0,1,2,3,10; never fabricated golden points."""
    fig,ax=plt.subplots(figsize=(6.4,5.1))
    _triangle(ax,"Hình 4.8 • Dãy điểm lặp thực tiến về A")
    _,points=trace_arrays(trace)
    xy=np.array([u_to_original(u) for u in points])
    ax.plot(xy[:,0],xy[:,1],"-",color=PALETTE["next"],lw=1,alpha=.65,label="Lịch sử solver thực")
    for k,offset in [(0,(-38,8)),(1,(-10,18)),(2,(5,-18)),(3,(8,8)),(10,(-35,16))]:
        if k>=len(xy):
            continue
        ax.plot(*xy[k],"o",color=PALETTE["next"],ms=4)
        ax.annotate(f"k={k}",xy[k],xytext=offset,textcoords="offset points",fontsize=8)
        if k>0:
            ax.annotate("",xy[k],xy[k-1],arrowprops={"arrowstyle":"->","color":PALETTE["next"]})
    ax.legend(loc="upper right",fontsize=8)
    fig.text(.1,.01,"Tái dựng theo Hình 4.8 • Các điểm k hữu hạn đều nằm trong miền.",fontsize=9)
    return fig


def plot_original_geometry():
    """[BC 4.4.2, unnumbered figure] Halfplane boundary labels and feasible side arrows."""
    fig,ax=plt.subplots(figsize=(6.5,5))
    _triangle(ax,"Mục 4.4.2 • Giải bài toán bằng hình học")
    ax.plot([-.1,2.2],[2.1,-.2],color="#233c50",label="$x_1+x_2=2$")
    ax.axhline(0,color="#233c50",lw=1)
    ax.axvline(0,color="#233c50",lw=1)
    for end,start in [((.8,.8),(1.1,1.1)),((.6,1.5),(.1,1.5)),((1.5,.6),(1.5,.1))]:
        ax.annotate("",end,start,arrowprops={"arrowstyle":"->","color":PALETTE["direction"]})
    ax.legend()
    fig.text(.1,.01,"Tái dựng hình không đánh số ở Mục 4.4.2 • z(O), z(A), z(B) = 2, 0, 2.",fontsize=9)
    return fig


def plot_histories(result):
    """[BC 4.4.10; MS NB53,8.5] Objective, potential and feasibility on separate figures."""
    from .potential import potential
    k,u=trace_arrays(result)
    values={"objective_vs_iteration":(2*u[:,1:].sum(axis=1),"Mục tiêu gốc z(k)"),
            "potential_vs_iteration":(np.array([potential(x,np.array([0.,1.,1.])) for x in u]),"Hàm thế Φ(k)"),
            "feasibility_residuals":(np.abs(u.sum(axis=1)-1),"Kiểm tra khả thi và tọa độ nhỏ nhất")}
    figures={}
    for name,(y,label) in values.items():
        fig,ax=plt.subplots(figsize=(7,3.7))
        ax.plot(k,y,color=PALETTE["current"],label="|Σu−1|" if name=="feasibility_residuals" else None)
        if name=="feasibility_residuals":
            ax.plot(k,u.min(axis=1),label="min(u)",color=PALETTE["direction"])
            ax.plot(k,np.zeros_like(k),ls="--",label="‖Au‖=0 (A rỗng)",color="#888888")
            ax.legend()
        ax.set(xlabel="Vòng lặp k",ylabel=label,title=label+" • Ví dụ 4.4, chạy thực")
        if name=="feasibility_residuals":
            ax.set_ylabel("Giá trị kiểm tra (min(u) không phải residual)")
        ax.grid(alpha=.2)
        figures[name]=fig
    return figures


def plot_benchmark(data,summary) -> dict:
    """[MS 8.5, DX] Actual time/iterations and failure counts; no complexity proof."""
    figures={}
    selected=summary[summary["case"].str.startswith("F2_")].sort_values("n")
    for key,column,title,ylabel in [("runtime_vs_n","median_ms","Thời gian đo thực theo n","Wall time (ms)"),
                                    ("iterations_vs_n","median_iter","Số vòng đo thực theo n","Vòng lặp")]:
        fig,ax=plt.subplots(figsize=(7,4))
        ax.plot(selected["n"],selected[column],"o-",label="Karmarkar • trung vị")
        if key=="runtime_vs_n":
            ax.plot(selected["n"],selected["reference_median_ms"],"s--",label="HiGHS dual simplex • trung vị")
        else:
            ax.plot(selected["n"],selected["reference_median_iter"],"s--",label="HiGHS báo số vòng (có presolve)")
        ax.set(xlabel="Số tọa độ n (nhóm F2)",ylabel=ylabel,title=title)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
        fig.subplots_adjust(bottom=.23)
        fig.text(.1,.005,"[DX] Khác tiêu chí dừng, backend và công việc mỗi vòng; không chứng minh độ phức tạp.",fontsize=8)
        figures[key]=fig
    fig,ax=plt.subplots(figsize=(9,4))
    counts=data["status"].value_counts()
    ax.barh(counts.index,counts.values,color=PALETTE["current"])
    ax.set(xlabel="Số lượt chạy (giữ cả lỗi và ca chưa hội tụ)",title="[DX] Trạng thái kết thúc của toàn bộ thực nghiệm")
    figures["termination_statuses"]=fig
    return figures

