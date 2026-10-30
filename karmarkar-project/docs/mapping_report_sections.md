# Đối chiếu nguồn và sản phẩm

[BC] là báo cáo 27 trang (trang in 33-59); [GD] là hợp đồng tính toán; [DX] là bổ sung kỹ thuật.
MasterSpec v3.0: C01-C12; notebook NB01-NB68. Dẫn nhập và cách đọc hình: NB01-NB05.

Các đường dẫn module ở `src/karmarkar/`, test ở `tests/`, hình ở `outputs/figures/`, bảng ở `outputs/tables/`.

| BC | Trang PDF / in | Notebook | Module | Kiểm tra | Bằng chứng |
|---|---|---|---|---|---|
| 4.1.1 | 2-3 / 34-35 | NB06-NB08 | plotting.py | test_example_44.py | figure_4_1; table_4_1_vertices |
| 4.1.2 | 3-4 / 35-36 | NB09-NB10 | examples.py,plotting.py | test_projective.py;test_example_44.py | figure_4_2 |
| 4.1.3 | 3-4 / 35-36 | NB11 | plotting.py + notebook | notebook run-all | overview_4_1_3 |
| 4.2.1 | 5-6 / 37-38 | NB12-NB14 | canonical.py,types.py | test_canonical.py | ValidationReport |
| 4.2.2 | 6-8 / 38-40 | NB15-NB16 | geometry.py | test_geometry.py | figure_4_3 |
| 4.2.3 | 8-9 / 40-41 | NB17-NB19 | projection.py | test_projection.py | figure_4_4 |
| 4.2.4 | 9-11 / 41-43 | NB20-NB23 | projective.py | test_projective.py | figure_4_5 |
| 4.2.5 | 12-13 / 44-45 | NB24-NB25 | iteration.py | test_iteration.py | figure_4_6 |
| 4.2.6 | 13-14 / 45-46 | NB26-NB27 | potential.py | test_potential.py | potential_history.csv |
| 4.2.7 | 14 / 46 | NB28 | solver.py (monitor) | test_stopping.py | Scope stated; theorem proof not re-proven |
| 4.2.8 | 14-16 / 46-48 | NB29 | notebook (theory) | notebook run-all | theoretical_iteration_bound; no runtime proof claim |
| 4.3.1 | 16 / 48 | NB30 | canonical.py,types.py | test_canonical.py | configs/default.yaml |
| 4.3.2 | 16-17 / 48-49 | NB31-NB34 | iteration.py | test_iteration.py | step_diagnostics.csv;source_example.json |
| 4.3.3 | 17 / 49 | NB35 | solver.py | test_stopping.py | source_full_history.csv |
| 4.3.4 | 18 / 50 | NB36 | plotting.py | notebook run-all; visual review | figure_4_7 |
| 4.3.5 | 18 / 50 | NB37 | solver.py,types.py | test_stopping.py;test_projection.py | StopReason and diagnostics |
| 4.4.1 | 19 / 51 | NB38 | examples.py | test_example_44.py | Original LP statement |
| 4.4.2 | 19-20 / 51-52 | NB39-NB40 | plotting.py,reporting.py | test_example_44.py | geometry_4_4_2;table_4_1_vertices |
| 4.4.3 | 20 / 52 | NB41-NB42 | examples.py | test_example_44.py | slack round-trip and z=2w |
| 4.4.4 | 21 / 53 | NB43 | geometry.py,projection.py | test_geometry.py;test_projection.py | P3 idempotence |
| 4.4.5 | 21-22 / 53-54 | NB44-NB45 | iteration.py | test_example_44.py::test_T26_first_step | actual step0 |
| 4.4.6 | 22-23 / 54-55 | NB46-NB47 | iteration.py,projective.py | test_example_44.py::test_T27_second_step | actual step1 |
| 4.4.7 | 23 / 55 | NB48 | iteration.py | test_example_44.py::test_T28_third_step | actual step2 |
| 4.4.8 | 23-24 / 55-56 | NB49-NB51 | examples.py,reporting.py | test_example_44.py::test_T29_closed_form_and_table | table_4_2_iterations |
| 4.4.9 | 24-25 / 56-57 | NB52 | plotting.py | notebook run-all; visual review | figure_4_8 from actual trace |
| 4.4.10 | 24-25 / 56-57 | NB53-NB55 | examples.py,potential.py | test_example_44.py::test_T30_potential_and_stopping | objective_vs_iteration;potential_history |
| 4.4.11 | 26 / 58 | NB56 | reporting.py | notebook run-all | table_4_3_methods |
| 4.5.1 | 26 / 58 | NB57 | iteration.py | test_iteration.py::test_T23_feasibility | min(u)>0; limit may be boundary |
| 4.5.2 | 27 / 59 | NB58 | projective.py,projection.py | test_projective.py;test_projection.py | Separate roles explained |
| 4.5.3 | 27 / 59 | NB59-NB68 | experiments.py,reporting.py | test_experiments.py | DX benchmark; limits; manifest |

## Từng phương trình (4.1)-(4.57)

| Công thức BC | Notebook | Thực hiện/kiểm tra |
|---|---|---|
| (4.1) | NB06-NB08 | Original LP; plotting.py; golden tests |
| (4.2) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.3) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.4) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.5) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.6) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.7) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.8) | NB12-NB14 | canonical.py,geometry.py; T01-T09; definitions in markdown |
| (4.9) | NB15-NB16 | geometry.py; T10; figure_4_3 |
| (4.10) | NB15-NB16 | geometry.py; T10; figure_4_3 |
| (4.11) | NB15-NB16 | geometry.py; T10; figure_4_3 |
| (4.12) | NB15-NB16 | geometry.py; T10; figure_4_3 |
| (4.13) | NB17-NB19 | projection.py; T16-T21; theory in markdown |
| (4.14) | NB17-NB19 | projection.py; T16-T21; theory in markdown |
| (4.15) | NB17-NB19 | projection.py; T16-T21; theory in markdown |
| (4.16) | NB17-NB19 | projection.py; T16-T21; theory in markdown |
| (4.17) | NB17-NB19 | projection.py; T16-T21; theory in markdown |
| (4.18) | NB20-NB23 | projective.py; T11-T15 |
| (4.19) | NB20-NB23 | projective.py; T11-T15 |
| (4.20) | NB20-NB23 | projective.py; T11-T15 |
| (4.21) | NB20-NB23 | projective.py; T11-T15 |
| (4.22) | NB20-NB23 | projective.py; T11-T15 |
| (4.23) | NB20-NB23 | projective.py; T11-T15 |
| (4.24) | NB24-NB25 | iteration.py; T22-T23; Cauchy-Schwarz explanation |
| (4.25) | NB24-NB25 | iteration.py; T22-T23; Cauchy-Schwarz explanation |
| (4.26) | NB24-NB25 | iteration.py; T22-T23; Cauchy-Schwarz explanation |
| (4.27) | NB24-NB25 | iteration.py; T22-T23; Cauchy-Schwarz explanation |
| (4.28) | NB24-NB25 | iteration.py; T22-T23; Cauchy-Schwarz explanation |
| (4.29) | NB26-NB27 | potential.py; T24-T25 |
| (4.30) | NB26-NB27 | potential.py; T24-T25 |
| (4.31) | NB26-NB27 | potential.py; T24-T25 |
| (4.32) | NB28 | solver.py optional monitor; theorem scope explained |
| (4.33) | NB29 | Theoretical bounds illustrated; no independent theorem proof or runtime guarantee |
| (4.34) | NB29 | Theoretical bounds illustrated; no independent theorem proof or runtime guarantee |
| (4.35) | NB29 | Theoretical bounds illustrated; no independent theorem proof or runtime guarantee |
| (4.36) | NB29 | Theoretical bounds illustrated; no independent theorem proof or runtime guarantee |
| (4.37) | NB31-NB34 | iteration.py; T22-T23,T31,T33 |
| (4.38) | NB31-NB34 | iteration.py; T22-T23,T31,T33 |
| (4.39) | NB31-NB34 | iteration.py; T22-T23,T31,T33 |
| (4.40) | NB31-NB34 | iteration.py; T22-T23,T31,T33 |
| (4.41) | NB31-NB34 | iteration.py; T22-T23,T31,T33 |
| (4.42) | NB38-NB40 | examples.py; Table 4.1 |
| (4.43) | NB38-NB40 | examples.py; Table 4.1 |
| (4.44) | NB41-NB42 | examples.py; original/canonical round-trip |
| (4.45) | NB41-NB42 | examples.py; original/canonical round-trip |
| (4.46) | NB41-NB42 | examples.py; original/canonical round-trip |
| (4.47) | NB43 | geometry.py,projection.py; T10,T16 |
| (4.48) | NB43 | geometry.py,projection.py; T10,T16 |
| (4.49) | NB44-NB45 | actual step0; T26 |
| (4.50) | NB44-NB45 | actual step0; T26 |
| (4.51) | NB44-NB45 | actual step0; T26 |
| (4.52) | NB46-NB47 | actual step1; T27 |
| (4.53) | NB48 | actual step2; T28 |
| (4.54) | NB49-NB52 | examples.py independent oracle vs actual trace; T29 |
| (4.55) | NB49-NB52 | examples.py independent oracle vs actual trace; T29 |
| (4.56) | NB53-NB54 | potential.py,examples.py; T30 |
| (4.57) | NB55 | minimum_example_iterations; T30 |

## Hình và bảng

- Hình 4.1: NB07; `outputs/figures/figure_4_1.png` và `.svg`.
- Hình 4.2: NB10; `outputs/figures/figure_4_2.png` và `.svg`.
- Hình 4.3: NB16; `outputs/figures/figure_4_3.png` và `.svg`.
- Hình 4.4: NB18; `outputs/figures/figure_4_4.png` và `.svg`.
- Hình 4.5: NB22; `outputs/figures/figure_4_5.png` và `.svg`.
- Hình 4.6: NB25; `outputs/figures/figure_4_6.png` và `.svg`.
- Hình 4.7: NB36; `outputs/figures/figure_4_7.png` và `.svg`.
- Hình 4.8: NB52; `outputs/figures/figure_4_8.png` và `.svg`.
- Hình không đánh số ở 4.4.2: NB39; `geometry_4_4_2.png/svg`.
- Bảng 4.1: NB40; `table_4_1_vertices.csv`.
- Bảng 4.2: NB51; `table_4_2_iterations.csv`.
- Bảng 4.3: NB56; `table_4_3_methods.csv`.

## Trạng thái và chứng cứ nghiệm thu

Chỉ đánh dấu PASS dựa trên `outputs/verification.json`, `outputs/pytest.xml`, `outputs/notebook_audit.json` và ảnh kiểm tra trực quan. Không coi bảng mapping này là bằng chứng một test đã chạy.
