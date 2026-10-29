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
| C12 | D에서 M(p,q)=1 ⇔ q=1, 또는 (q ≥ 3/2 − p 이고 q ≥ 1 − p/3) | **증명됨** (2026-10-29: 정리 C1·C2(k = n−2)의 따름, `notes/proofs/exactness.md` §2). 이전 근거: 컴퓨터 보조(V18 facet) + 격자 | `results/regions/REGIONS.md` V18, `tests/test_regions.py::test_certainty_region` |
| C13 | q=3/5 단면은 조각 V16, V02, V12, V11을 지난다. 경계는 p=(√21−3)/10, 1/5, 1−√7/5다. 기존 상한은 p ∈ [0,1/5] ∪ {3/5}에서 정확하고, 1/5<p<3/5에서는 엄밀히 크다 | 정확 계산(sympy: 경계 좌표, 그리고 열린 구간에서 상한을 이루는 8개 이차식 어느 것도 M과 만나지 않음). 격자 p=(3/5)·k/60에서도 확인 | `tests/test_rn_bounds.py::test_slice_q_three_fifths_facts`, `results/regions/slice_q3_5.png` |
| C14 | (탐색) D의 60분할 격자에서 기존 상한과 M의 차이가 가장 큰 점은 (1/10, 5/6)이다. 상한 389/450, M 41/60, 차이 163/900 | 탐색 | journal J16 |

## 새 연구 질문: 두 모멘트 상한(BP)은 언제 정확한가 (일반 n, k; 2026-10-29~)

배경과 선택 이유는 `notes/research_reassessment.md`, 증명은 `notes/proofs/exactness.md`(§ 번호)에 있다. P̄(n,k,p) = max P(S≥k), LOO_j = Σ_{l≠j} p_l이다.

| ID | 주장 | 상태 | 근거 |
|---|---|---|---|
| C15 | (보조정리 1) 쌍별 독립이면 E[S∣X_j=1] = 1+LOO_j, E[S∣X_j=0] = LOO_j. (보조정리 M) P̄는 각 p_j에 대해 비감소 | **증명됨** | exactness §1, `tests/test_exactness.py::test_conditional_mean_identity_on_an_exact_law`, `::test_monotonicity_float`(부동소수점 교차확인) |
| C16 | (정리 C1·C2) P̄=1이면 p_j<1인 모든 j에서 LOO_j ≥ k. 역은 k ∈ {1, n−2, n−1, n}과 동일 주변확률에서 성립. k=n−2는 새 명시적 구성 | **증명됨** (k=1·동일은 R–N 재현) | exactness §2, `::test_top2_complement_law_is_exact_and_certain` |
| C17 | (추측 C) 모든 n, k에서 P̄=1 ⇔ p_j<1인 모든 j에서 LOO_j ≥ k | **추측** | 부동소수점 증거 4,000점 이상(수치 허용오차 사례 155점 제외 불일치 0), `results/runs/explore-exactness/`, `::test_certainty_criterion_float`. 실패한 증명 경로: research_reassessment §6 |
| C18 | (E2·E3·E4·E2′·E5) BP-최적 지지가 유일한 K일 때 정확성의 필요조건: 조건부 평균 구간, {0,k,n}의 두 근 경직성, 층 위 법칙, 2-그룹 집계, 순서 기반 상한의 부분문제 환원 | **증명됨** | exactness §3, §6 |
| C19 | E2와 E2′(모든 2-분할)는 충분하지 않다: n=4, k=3, p=(13/20,19/50,3/4,17/50); n=5, k=4, p=(29/100,2/5,13/25,23/25,33/50) | **정확 계산 검증** (정확 Farkas 이차식) | exactness §3, `::test_interval_condition_is_not_sufficient`, `::test_two_group_split_conditions_are_not_sufficient` |
| C20 | (정리 S) P̄ = S₂/C(k,2) ⇔ (I) LOO_j ≤ k−1 (p_j>0), (II) (p_ip_j)의 분수 K_k-분해, (III) 1 − S₁ + 2S₂/k ≥ 0. 따름: P̄(n,2,p) = S₂ ⇔ max_{p_j>0} LOO_j ≤ 1 | **증명됨** (동일 주변확률이면 R–N Prop. 4.3(b) 재현) | exactness §4, `::test_second_moment_term_exactness_float`, `::test_petersen_formula_for_second_moment_term` |
| C21 | (보조정리 L1) n ≥ 4에서 세 층 합집합의 모멘트 아핀 껍질이 전체가 아님 ⇔ K = {0,s,n}(2≤s≤n−2) 또는 K ⊆ {0,1,n−1,n}. (정리 L) 동일 주변확률 근방에서 BP의 정확성은 비예외 지지에서 열린 집합으로 안정적이고, 예외 지지(특히 R–N 경우 (b) {0,k,n})에서는 진부분 대수집합으로 제한된다 | **증명됨** (L1은 Gottlieb–Kantor–Wilson 포함행렬 rank 정리 인용, n ≤ 8 정확 계산과 일치) | exactness §5, `::test_layer_kernel_classification` |
| C22 | R–N Example 3.2(n=12)의 비순서·순서 기반 BP 24칸의 정확/비정확이 E1–E5로 모두 설명된다 | **정확 계산 검증** (정확한 법칙 또는 정확한 조건 위반. 생성 코드 안의 정확 검사이며 독립 검증기는 아님) | exactness §7.1, `results/exactness/rn_example_3_2.md`, `::test_rn_example_3_2_verdicts` |
| C23 | 2+3 문제의 따름정리 C(i): V02(정리 S), V16(E2+법칙), V18(C2)에서 정확. V10·V11·V12·V14·V21은 E3(p+2q≠2), V15는 E4, V19·V20은 E2로 비정확 | **정확 계산 검증** | exactness §7.2, `::test_two_three_pieces_explained_by_criteria`, `::test_rigidity_line_in_the_two_three_family` |
| C24 | (탐색) Example 3.2에서 모든 2-분할 집계 상한의 최솟값은 k=5에서 0.99623, k=6에서 0.90178로 R–N 순서 기반 상한(1, 0.92538)보다 작다 | 탐색 | research_reassessment §7, journal J19 |

## 실패 접근

| 접근 | 목적 | 실패 원인 | 기록 |
|---|---|---|---|
| 최대(또는 최소) 좌표로 조건화하는 귀납 | 추측 C 증명 | 조건부 법칙의 쌍 확률이 곱 꼴이 아니게 되어 귀납 가정이 닫히지 않음 | research_reassessment §6, J19 |
| 고차 모멘트를 곱 꼴(λ_{|T|} Π q)로 두는 구성 | 추측 C의 명시적 구성 | 경계점 236개 모두 실패 | `scripts/explore_exactness.py productform` |
| 2n개 조건부 평균 부등식에 의한 Positivstellensatz | 추측 C를 일반 모멘트 점으로 강화 | 곱 꼴이 아닌 점에서는 거짓(반례 다수) | `... positivstellensatz` |
| 두 값 주변확률의 "P(B=β) 최대화" 구성 | 두 값 경우 증명 | 11%에서 1차원 모멘트 조건 실패(구성 선택의 실패) | `... twovalued` |
| k=2 일반 닫힌꼴의 단순 후보식 | Q2 | n ≥ 4에서 틀림 | `... k2` |
