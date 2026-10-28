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
| C2 | 32상태 LP와 12상태 LP의 최적값이 같고, 최적해가 복원 사상으로 대응한다 | 추측(증명 작성 예정) | 계획 1.3절 |
| C3 | M(p,q) = min_{y∈V} Q_y(p,q), V는 21개의 쌍대 꼭짓점 | 정확 계산 검증(표본점), 증명 작성 예정 | 꼭짓점 21개는 전수열거로 정확히 얻음(`tests/test_exact.py::test_enumeration_counts`). 무작위 유리점 15곳에서 세 정확 경로 일치(`test_three_exact_routes_agree`) |
| C4 | M은 p↔q에 대해 대칭이 아니다: M(2/5,3/5)=61/75, M(3/5,2/5)=19/25 | **정확 계산 검증** | 두 점의 증서가 검증기 PASS (`tests/test_exact.py`), `tests/test_crosscheck.py::test_not_symmetric_in_p_and_q` |
| C5 | p=q 단면에서 12상태 값 = 단변수 S 이항모멘트 LP 값 | 정확 계산 검증(p=k/97, 98점) | `tests/test_crosscheck.py::test_diagonal_matches_fully_symmetric_model`. p=q이면 S₅ 대칭화로 두 모형이 같은 LP의 축소이므로 정리로도 성립(R–N Thm 4.1 증명과 같은 논법) |
| C6 | M(0,q)=q² (q≤1/2), 1−3q+3q² (q≥1/2); M(p,1)=1 | 정확 계산 검증(61점) + 문헌 정리로 증명 | p=0이면 X1=X2=0이라 R–N Thm 4.1(n=k=3)로 귀결. q=1이면 X3=X4=X5=1. `tests/test_crosscheck.py::test_edge_*` |
| C7 | 두 모멘트(S1,S2)만 쓰는 상한(=R–N 비순서 BP)은 대표점에서 107/125로 tight하지 않다 | 정확 계산 검증 | `tests/test_crosscheck.py::test_two_moment_relaxation_is_strictly_looser_at_representative_point` |

## 실패 접근

(아직 없음)
