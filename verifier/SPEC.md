# 검증기 명세 (point 모드, 형식 `pw5-point/v1`)

이 문서는 `verifier/verify.py`보다 먼저 작성되었고, 검증기는 이 문서만을 근거로 구현한다.
검증기는 최적화 코드(`src/pwbound`)를 import하지 않으며, Python 표준 라이브러리만 쓴다.

> 상태: AI 작성 초안. **사람 검토 전** (검토 후 이 줄을 검토자·날짜로 바꾼다).

## 1. 무엇을 증명하는가

증서는 고정된 (p, q)에 대해 다음 세 가지를 담는다.

1. 32상태 분포 μ (하한 증거)
2. 32상태 쌍대 계수 (u0, u_i, u_ij) (상한 증거)
3. 주장값 V

검증기가 아래 검사를 모두 통과시키면 다음이 성립한다.

- μ는 실행 가능하다. 따라서 M(p,q) ≥ P_μ(S≥3) = V이다.
- 모든 x∈{0,1}^5에서 g(x) = u0 + Σ u_i x_i + Σ_{i<j} u_ij x_i x_j ≥ 1[|x|≥3]이다. 이때 임의의 실행 가능 분포 ν에 대해 다음이 성립한다(약쌍대성).
  - P_ν(S≥3) ≤ E_ν[g(X)] = u0 + Σ u_i p_i + Σ u_ij p_i p_j = V
  - 둘째 등호는 실행 가능성에서 E[X_i]=p_i, E[X_iX_j]=p_ip_j이기 때문이다.
  - 따라서 M(p,q) ≤ V이다.
- 그러므로 **M(p,q) = V이고 μ는 최대화 분포다.** 이 결론은 축소(12상태) 보조정리에 의존하지 않는다.

증서에 담긴 12상태 부분(`reduced`)은 축소 모형 자체의 증서로 따로 검사한다(§4.4). 그리고 32상태 부분과의 정합성을 검사한다(§4.5).

## 2. 고정된 문제 정의

- 변수 X1..X5. 그룹 G1 = {1,2}, G2 = {3,4,5}.
- 목표 주변확률: p_1=p_2=p, p_3=p_4=p_5=q.
- 쌍 10개: (i,j), 1≤i<j≤5.
- 목적 사건: S = X1+…+X5 ≥ 3 (threshold = 3).
- 32상태 키: 길이 5의 `0`/`1` 문자열. **왼쪽 첫 글자가 X1**이다.
- 12상태 키: `"a,b"` (a∈{0,1,2}, b∈{0,1,2,3}). a = X1+X2, b = X3+X4+X5.

## 3. 입력 형식

### 3.1 JSON 파싱 규칙
- JSON의 부동소수점 숫자, `NaN`, `Infinity`는 거부한다.
- 중복 키는 거부한다(어느 깊이든).
- 정수 리터럴은 `problem.groups`와 `problem.threshold`에서만 허용한다.
- 모든 유리수는 문자열이며 정규식 `^-?[0-9]+(/[1-9][0-9]*)?$`(ASCII 숫자만)를 만족해야 한다.
  - 따라서 `"0.4"`, `"1e-3"`, `"nan"`, `"1_000"`, `" 1/2"`는 모두 거부된다.
  - 분모가 0인 값과 `"1/0"`도 거부된다.

### 3.2 최상위 구조 (키 집합이 정확히 일치해야 함)

```json
{
  "format": "pw5-point/v1",
  "problem": {"p": "2/5", "q": "3/5", "groups": [[1,2],[3,4,5]], "threshold": 3},
  "claim": {"value": "61/75"},
  "primal": {
    "reduced": {"0,0": "...", ... 12개},
    "lifted":  {"00000": "...", ... 32개}
  },
  "dual": {
    "reduced": {"y0": "...", "y1": "...", "y2": "...", "y3": "...", "y4": "...", "y5": "..."},
    "lifted": {
      "const": "...",
      "x":  {"1": "...", ..., "5": "..."},
      "xx": {"1,2": "...", "1,3": "...", ... 10개, i<j}
    }
  },
  "provenance": { ... 자유 형식, 검증하지 않음 ... }
}
```

- `provenance`는 사람을 위한 기록이다. 검증기는 이를 읽지 않고 신뢰하지도 않는다.
- 기저(basis) 정보가 들어 있어도 쓰지 않는다.
- 키가 빠지거나 남으면 형식 오류다.

## 4. 검사 항목과 코드

각 검사는 `PASS`/`FAIL`과 코드, 실패 시 상세(어느 상태·어느 쌍인지)를 출력한다.

### 4.1 형식 (실패 시 이후 검사를 하지 않음, 종료 코드 2)
| 코드 | 내용 |
|---|---|
| `E_JSON` | JSON 파싱 실패, float/NaN/Infinity, 중복 키 |
| `E_FORMAT` | `format` 값 불일치, 최상위·하위 키 집합 불일치 |
| `E_RATIONAL` | 유리수 문자열 규칙 위반 |
| `E_PROBLEM` | `groups ≠ [[1,2],[3,4,5]]` 또는 `threshold ≠ 3` |

### 4.2 영역
| 코드 | 내용 |
|---|---|
| `E_RANGE` | p 또는 q가 [0,1] 밖 (형식 오류로 취급, 종료 코드 2) |
| `SCOPE` | 0 ≤ p ≤ q ≤ 1. `--allow-outside-scope`가 있으면 p>q도 허용(비대칭 비교용) |

### 4.3 32상태 원·쌍대 (핵심)
| 코드 | 내용 |
|---|---|
| `P_NONNEG` | 모든 μ(x) ≥ 0 |
| `P_TOTAL` | Σ μ(x) = 1 |
| `P_MARGINAL_i` (i=1..5) | Σ_{x_i=1} μ(x) = p_i |
| `P_PAIR_i_j` (10개) | 네 칸 (s,t)∈{0,1}² 모두 P(X_i=s, X_j=t) = P*(X_i=s)·P*(X_j=t). P*는 **목표** 주변확률 p_i이다 |
| `P_OBJECTIVE` | Σ_{|x|≥3} μ(x) = claim.value |
| `D_DOMINATE` | 32개 x 모두 g(x) ≥ 1[|x|≥3]. 실패 시 위반 상태와 g(x) 출력 |
| `D_VALUE` | u0 + Σ u_i p_i + Σ u_ij p_i p_j = claim.value |

### 4.4 12상태 원·쌍대 (축소 모형 증서)
| 코드 | 내용 |
|---|---|
| `R_NONNEG` | 모든 π(a,b) ≥ 0 |
| `R_MOMENTS` | Σπ=1, E[A]=2p, E[B]=3q, E[A(A−1)]=2p², E[B(B−1)]=6q², E[AB]=6pq |
| `R_OBJECTIVE` | Σ_{a+b≥3} π(a,b) = claim.value |
| `R_DOMINATE` | 12점 모두 f(a,b)=y0+y1·a+y2·b+y3·a(a−1)+y4·b(b−1)+y5·ab ≥ 1[a+b≥3] |
| `R_VALUE` | y0+2p·y1+3q·y2+2p²·y3+6q²·y4+6pq·y5 = claim.value |

### 4.5 정합성 (12상태 ↔ 32상태)
| 코드 | 내용 |
|---|---|
| `C_PROJECT` | 각 (a,b)에서 Σ_{x: x1+x2=a, x3+x4+x5=b} μ(x) = π(a,b) |
| `C_DUAL_LIFT` | `dual.lifted`가 `dual.reduced`의 복원과 같다. const=y0. x_1=x_2=y1. x_3=x_4=x_5=y2. xx_{1,2}=**2·y3**. xx_{3,4}=xx_{3,5}=xx_{4,5}=**2·y4**. 교차 6쌍은 xx=**y5** |

`C_DUAL_LIFT`의 근거: x_i² = x_i이므로 다음이 성립한다.
- a(a−1) = 2·x1x2
- b(b−1) = 2·(x3x4+x3x5+x4x5)
- ab = Σ_{i∈G1, j∈G2} x_i x_j

## 5. 출력과 종료 코드
- 표준출력: 검사마다 한 줄씩 `PASS <코드>` 또는 `FAIL <코드>: <상세>`를 쓴다. 마지막 줄은 `VERDICT: PASS` 또는 `VERDICT: FAIL`이다.
- `--json`: 같은 내용을 JSON으로 출력한다(`{"verdict":..., "checks":[{"code":..., "ok":..., "detail":...}]}`).
- 종료 코드: 0 = 모든 검사 PASS, 1 = 하나 이상 FAIL, 2 = 형식·파싱 오류(§4.1, `E_RANGE`).
- 판정: §4.2(`SCOPE`)–§4.5의 모든 검사가 PASS일 때만 `VERDICT: PASS`다.

## 6. 실행 방법
```bash
python -I verifier/verify.py <certificate.json> [--json] [--allow-outside-scope]
```
`-I`(격리 모드)로 실행해 현재 디렉터리와 사용자 site-packages의 코드가 섞이지 않게 한다.

## 7. 독립성 규칙 (테스트로 강제)
- import 허용 목록: `argparse`, `collections`, `fractions`, `itertools`, `json`, `re`, `sys`
- 금지: float 리터럴, `float(`, `eval`, `exec`, `compile`, `__import__`, 상대 import, `pwbound` import

## 8. 이후 확장 (region 모드, 형식 `pw5-region/v1`)
정리 A·B 단계에서 추가한다. 다항식 항등식은 (p,q)의 차수 ≤ 2 단항식 dict 연산으로 표준 라이브러리만 써서 검사한다.
