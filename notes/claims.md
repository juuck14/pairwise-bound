# 주장 상태표

상태 정의:
- **증명됨**: `notes/proofs/`에 사람이 읽을 수 있는 증명이 있고, 가능한 부분은 테스트로 고정됨.
- **정확 계산 검증**: 독립 검증기(`verifier/verify.py`)가 Fraction 정확 계산으로 PASS한 증서가 있음.
- **탐색**: 부동소수점, 격자, 일회성 계산 등으로만 관찰됨. 주장으로 쓰지 않음.
- **추측**: 근거가 부분적임.
- **반례**: 반박됨.
- **실패 접근**: 시도했으나 막힌 접근(원인 기록).

| ID | 주장 | 상태 | 근거 |
|---|---|---|---|
| C1 | M(2/5,3/5) = 61/75 | **정확 계산 검증** | 독립 검증기 PASS: `tests/test_verifier.py::test_seed_certificate_*` (32상태 원·쌍대 일치). 검증기 SPEC은 사람 검토 완료(2026-10-29) |
| C2 | 32상태 LP와 12상태 LP의 최적값이 같고, 최적해가 복원 사상으로 대응한다(정리 R). 쌍대도 대응한다(명제 D) | **증명됨** (기법은 R–N Thm 4.1 증명의 응용) | `notes/proofs/reduction.md`; 계산 보조: `tests/test_model.py`, `tests/test_crosscheck.py::test_highs_full_and_reduced_match_exact` |
| C3 | **정리 A**: [0,1]² 전체에서 M(p,q) = min_{y∈V} Q_y(p,q), V는 21개의 쌍대 꼭짓점 | **증명됨(컴퓨터 보조)** | `notes/proofs/theorem_AB.md`. 검증기 `RG_RANK`, `RG_FEASIBLE`, `RG_VERTICES`가 영역 증서에서 PASS. 보조: 세 정확 경로 일치(`tests/test_exact.py`) |
| C4 | M은 p↔q에 대해 대칭이 아니다: M(2/5,3/5)=61/75, M(3/5,2/5)=19/25 | **정확 계산 검증** | 두 점의 증서가 검증기 PASS (`tests/test_exact.py`), `tests/test_crosscheck.py::test_not_symmetric_in_p_and_q` |
| C5 | p=q 단면에서 12상태 값 = 단변수 S 이항모멘트 LP 값 | 정확 계산 검증(p=k/97, 98점) | `tests/test_crosscheck.py::test_diagonal_matches_fully_symmetric_model`. p=q이면 S₅ 대칭화로 두 모형이 같은 LP의 축소이므로 정리로도 성립(R–N Thm 4.1 증명과 같은 논법) |
| C6 | M(0,q)=q² (q≤1/2), 1−3q+3q² (q≥1/2); M(p,1)=1 | 정확 계산 검증(61점) + 문헌 정리로 증명 | p=0이면 X1=X2=0이라 R–N Thm 4.1(n=k=3)로 귀결. q=1이면 X3=X4=X5=1. `tests/test_crosscheck.py::test_edge_*` |
| C7 | 두 모멘트(S1,S2)만 쓰는 상한(=R–N 비순서 BP)은 대표점에서 107/125로 tight하지 않다 | 정확 계산 검증 | `tests/test_crosscheck.py::test_two_moment_relaxation_is_strictly_looser_at_representative_point` |

| C8 | **정리 B**: 0<p<q<1에서 내부 활성 조각은 정확히 11개(V02, V10, V11, V12, V14, V15, V16, V18, V19, V20, V21). 각 조각의 영역은 원뿔 facet 이차 부등식으로 주어지고, 달성분포는 (p,q)의 다항식이다 | **증명됨(컴퓨터 보조)** | `notes/proofs/theorem_AB.md`, `results/regions/region_certificate.json`(검증기 54/54 PASS), `results/regions/REGIONS.md`, `tests/test_regions.py` |
| C9 | **따름정리 C (2026-10-29 정정)**: D에서 각 상한이 M과 같아지는 집합은 (i) BP형(비순서 BP, 순서 기반 BP, §3.2 강화판): R_V02 ∪ R_V16 ∪ R_V18 ∪ Z, (ii) SSS형(비순서·순서 기반·강화판): R_V02 ∪ R_V18 ∪ Z′, (iii) Chebyshev형(비순서·순서 기반·강화판): R_V18 ∪ Z″ (Z, Z′, Z″는 내부 없음). **정정 전 판은 SSS·Chebyshev도 (i)과 같은 집합에서 tight하다고 썼으나 틀렸다**: (1/7,4/7)에서 M=BP=24/49, SSS=73/147, Chebyshev=48/97 | **증명됨(컴퓨터 보조)**. (i)은 기존 논증, (ii)(iii)은 정정 때 추가한 논증 | `notes/proofs/theorem_AB.md` 따름정리 C, `tests/test_rn_bounds.py::test_v16_witness_separates_the_three_bounds`, `::test_sss_and_chebyshev_tightness_at_witnesses`, `::test_sss_and_chebyshev_never_coincide_with_v02_v16_formulas` |
| C10 | 쌍대가 s=a+b만의 함수인 활성 조각은 V02(=C(s,2)/3, 비순서 SSS), V16(=(s−1)(s−2)/2, 1−S₁+S₂), V18(=1)뿐이다 | 정확 계산 검증 | `tests/test_rn_bounds.py::test_only_sum_only_vertices_carry_full_rank` |
| C11 | 조각 지도의 교점은 D 꼭짓점 3개와 교점 11개다. 네 조각이 만나는 점이 6개 있다. 예: (2/5,4/5)에서 V10/V11/V14/V15, (7/8−√33/8, 3/8+√33/24)에서 V02/V12/V16/V19 | 좌표와 "표의 조각들이 그 점에서 M을 정확히 달성"은 **정확 계산 검증**(sympy, `tests/test_junctions.py`). 교점 목록이 빠짐없는지와 인접 판정은 **탐색**(반지름 1e-4 원 표본) | `results/regions/JUNCTIONS.md`, `scripts/junctions.py` |
| C12 | D에서 M(p,q)=1 ⇔ q=1, 또는 (q ≥ 3/2 − p 이고 q ≥ 1 − p/3) | 컴퓨터 보조 증명(V18 facet 부등식에서 유도) + 격자 확인 | `results/regions/REGIONS.md` V18, `tests/test_regions.py::test_certainty_region` |
| C13 | q=3/5 단면은 조각 V16, V02, V12, V11을 지난다. 경계는 p=(√21−3)/10, 1/5, 1−√7/5다. 기존 상한은 p ∈ [0,1/5] ∪ {3/5}에서 정확하고, 1/5<p<3/5에서는 엄밀히 크다 | 정확 계산(sympy: 경계 좌표, 그리고 열린 구간에서 상한을 이루는 8개 이차식 어느 것도 M과 만나지 않음). 격자 p=(3/5)·k/60에서도 확인 | `tests/test_rn_bounds.py::test_slice_q_three_fifths_facts`, `results/regions/slice_q3_5.png` |
| C14 | (탐색) D의 60분할 격자에서 기존 상한과 M의 차이가 가장 큰 점은 (1/10, 5/6)이다. 상한 389/450, M 41/60, 차이 163/900 | 탐색 | journal J16 |

## 실패 접근

(아직 없음)
