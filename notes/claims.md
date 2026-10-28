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
| C1 | M(2/5,3/5) = 61/75 | **정확 계산 검증** | 독립 검증기 PASS: `tests/test_verifier.py::test_seed_certificate_*` (32상태 원·쌍대 일치). 검증기 SPEC은 사람 검토 전 |
| C2 | 32상태 LP와 12상태 LP의 최적값이 같고, 최적해가 복원 사상으로 대응한다(정리 R). 쌍대도 대응한다(명제 D) | **증명됨** (기법은 R–N Thm 4.1 증명의 응용) | `notes/proofs/reduction.md`; 계산 보조: `tests/test_model.py`, `tests/test_crosscheck.py::test_highs_full_and_reduced_match_exact` |
| C3 | **정리 A**: [0,1]² 전체에서 M(p,q) = min_{y∈V} Q_y(p,q), V는 21개의 쌍대 꼭짓점 | **증명됨(컴퓨터 보조)** | `notes/proofs/theorem_AB.md`. 검증기 `RG_RANK`, `RG_FEASIBLE`, `RG_VERTICES`가 영역 증서에서 PASS. 보조: 세 정확 경로 일치(`tests/test_exact.py`) |
| C4 | M은 p↔q에 대해 대칭이 아니다: M(2/5,3/5)=61/75, M(3/5,2/5)=19/25 | **정확 계산 검증** | 두 점의 증서가 검증기 PASS (`tests/test_exact.py`), `tests/test_crosscheck.py::test_not_symmetric_in_p_and_q` |
| C5 | p=q 단면에서 12상태 값 = 단변수 S 이항모멘트 LP 값 | 정확 계산 검증(p=k/97, 98점) | `tests/test_crosscheck.py::test_diagonal_matches_fully_symmetric_model`. p=q이면 S₅ 대칭화로 두 모형이 같은 LP의 축소이므로 정리로도 성립(R–N Thm 4.1 증명과 같은 논법) |
| C6 | M(0,q)=q² (q≤1/2), 1−3q+3q² (q≥1/2); M(p,1)=1 | 정확 계산 검증(61점) + 문헌 정리로 증명 | p=0이면 X1=X2=0이라 R–N Thm 4.1(n=k=3)로 귀결. q=1이면 X3=X4=X5=1. `tests/test_crosscheck.py::test_edge_*` |
| C7 | 두 모멘트(S1,S2)만 쓰는 상한(=R–N 비순서 BP)은 대표점에서 107/125로 tight하지 않다 | 정확 계산 검증 | `tests/test_crosscheck.py::test_two_moment_relaxation_is_strictly_looser_at_representative_point` |

| C8 | **정리 B**: 0<p<q<1에서 내부 활성 조각은 정확히 11개(V02, V10, V11, V12, V14, V15, V16, V18, V19, V20, V21). 각 조각의 영역은 원뿔 facet 이차 부등식으로 주어지고, 달성분포는 (p,q)의 다항식이다 | **증명됨(컴퓨터 보조)** | `notes/proofs/theorem_AB.md`, `results/regions/region_certificate.json`(검증기 54/54 PASS), `results/regions/REGIONS.md`, `tests/test_regions.py` |
| C9 | **따름정리 C**: R–N의 두 모멘트 BP 상한과 Theorem 3.1 순서 기반 상한(§3.2 강화 포함, SSS·Chebyshev도)은 D에서 R_V02 ∪ R_V16 ∪ R_V18 ∪ Z(내부 없음)에서만 tight하다. 나머지 8개 조각 내부(Z 제외)에서는 엄밀히 느슨하다 | **증명됨(컴퓨터 보조)** | `notes/proofs/theorem_AB.md` 따름정리 C, `tests/test_rn_bounds.py` |
| C10 | 쌍대가 s=a+b만의 함수인 활성 조각은 V02(=C(s,2)/3, 비순서 SSS), V16(=(s−1)(s−2)/2, 1−S₁+S₂), V18(=1)뿐이다 | 정확 계산 검증 | `tests/test_rn_bounds.py::test_only_sum_only_vertices_carry_full_rank` |
| C11 | 조각 경계의 삼중점 좌표(예: (0,2/3), (1/2,1), (1/2,1/2), (2/5,4/5), (3/4,3/4)) | 탐색(그림 관찰) | `results/regions/region_map.png` |

## 실패 접근

(아직 없음)
