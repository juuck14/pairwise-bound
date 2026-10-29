# 11/1 데모 제출 안내

KAIST 「인공지능기반수학발견」 개인 Math Research 과제의 데모 코드다.

## 무엇을 보여 주는가

X1, …, X5 ∈ {0,1}이 다음 조건을 만족한다.
- P(X1=1)=P(X2=1)=p, P(X3=1)=P(X4=1)=P(X5=1)=q
- 모든 쌍이 독립이다(다섯 변수 전체의 상호 독립은 가정하지 않음).

이때 데모는 다음 값을 **정확한 분수로** 계산하고, 그 값이 최댓값임을 **스스로 증명하는 증서**를 함께 출력한다.

M(p,q) = max P(X1+…+X5 ≥ 3)

- **하한 증거:** 값을 실제로 달성하는 유리수 결합분포(32개 상태의 확률)
- **상한 증거:** 모든 상태에서 사건 지시함수 이상인 2차 쌍대 다항식. 그 기댓값이 같은 값이다.
- **검증:** 최적화 코드와 분리된 검증기(표준 라이브러리만 사용)가 두 증거를 정확한 유리수 계산으로 검사한다. 두 값이 같으면 최적성이 증명된다.

대표 사례 p=2/5, q=3/5의 결과는 **61/75**다.

## 실행 방법

필요한 것: Python 3.11 이상(3.11, 3.12, 3.13에서 확인), CPU만 사용. 네트워크 접속과 LLM API 호출은 없다.

```bash
python3 -m venv .venv
```

```bash
. .venv/bin/activate
```
(Windows PowerShell: `.venv\Scripts\Activate.ps1`)

```bash
pip install -r requirements.txt
```

```bash
python -m scripts.demo
```

다른 입력값(유리수)으로도 실행할 수 있다.

```bash
python -m scripts.demo --p 1/5 --q 1/2
```

실행하지 않고 볼 수 있도록 대표 사례의 출력을 [`results/demo_output.txt`](results/demo_output.txt)에 저장해 두었다.

## 출력 읽는 법 (대표 사례)

| 출력 절 | 내용 |
|---|---|
| `Maximum` | M(2/5,3/5) = 61/75 ≈ 0.8133. 이 점이 속한 조각 이름(V12) |
| `Maximizing distribution, 12-state model` | A=X1+X2, B=X3+X4+X5의 결합분포 6개 항. 대칭성 덕분에 32상태 문제를 12상태로 줄일 수 있다(증명: `notes/proofs/reduction.md`) |
| `Lifted 32-state distribution` | 위 분포를 원래 32개 상태로 되돌린 것. 17개 상태가 양의 확률을 가진다 |
| `Upper-bound certificate` | 쌍대 다항식 f(a,b) = a − (1/3)a(a−1) + (1/6)b(b−1) − (1/6)ab. 12개 점 모두에서 f ≥ 1[a+b≥3]이고, 기댓값은 이차식 Q(p,q) = 2p − (2/3)p² + q² − pq = 61/75다. 32상태 형태의 계수도 함께 출력한다 |
| `Cross-checks` | 부동소수점 LP 해법(HiGHS)으로 32상태·12상태 문제를 따로 풀어 비교한다(차이 ≈ 1e-16). 기존 두 모멘트 상한(107/125)과도 비교한다 |
| `Independent verifier` | 증서 파일을 쓰고, 검증기를 별도 프로세스(`python -I`)로 실행한 결과. 28/28 검사 PASS |

검증기의 28개 검사는 다음과 같다.
- 범위(1개): 0 ≤ p ≤ q ≤ 1
- 32상태 분포(8개): 비음수, 총확률, 다섯 주변확률, 목적값
- 10쌍 독립(10개): 쌍마다 2×2 네 칸 모두
- 32상태 쌍대(2개): 32개 상태 모두에서 지배, 쌍대값 = 주장값
- 12상태 증서(5개): 비음수, 모멘트 조건, 목적값, 12점 지배, 쌍대값
- 두 수준의 정합성(2개): 32상태 분포를 사영하면 12상태 분포, 32상태 쌍대가 12상태 쌍대의 복원

명세는 [`verifier/SPEC.md`](verifier/SPEC.md)에 있다.

## 추가로 실행해 볼 수 있는 것

| 명령 | 내용 | 이 환경에서 잰 시간 |
|---|---|---|
| `python -m scripts.demo` | 대표 사례 데모 | 약 1초 |
| `python -I verifier/verify.py results/certificates/p2_5-q3_5.json` | 저장된 증서만 독립 검증 | 1초 미만 |
| `python -m scripts.classify` | 0≤p≤q≤1 전체의 조각 분류 증서 생성 + 검증(54개 검사) | 약 10초 |
| `python -m scripts.plot_regions` | 조각 지도 그림 | 약 8초 |
| `python -m scripts.plot_slice` | q=3/5 단면 비교 그림 | 약 4초 |
| `pytest` | 전체 테스트 1000개 | 18–25초 |

## 현재까지의 결과 요약

| 결과 | 상태 |
|---|---|
| M(2/5,3/5) = 61/75 | 독립 검증기 PASS |
| 32상태 문제 ⇔ 12상태 (A,B) 문제 (그룹 내부 순열 평균화) | 증명 |
| 0≤p≤q≤1에서 M(p,q)는 11개 조각으로 나뉜 조각별 이차식이다. 조각마다 공식, 영역(이차 부등식), 달성분포(다항식)를 구했다 | 컴퓨터 보조 증명, 독립 검증기 54/54 PASS |
| 기존 상한(Ramachandra–Natarajan) 중 가장 강한 BP형은 11개 중 3개 조각(V02, V16, V18)에서만 정확하다. SSS형은 2개(V02, V18), Chebyshev형은 1개(V18) 조각에서만 정확하다 (2026-10-29 정정, `notes/claims.md` C9) | 컴퓨터 보조 증명 |
| p와 q를 바꾸면 값이 달라진다: M(3/5,2/5) = 19/25 | 정확 계산 |

> 2026-10-29 연구 방향 재평가: 위 결과는 표준 도구로 한 사례를 정확히 푼 것이라는 평가에 따라, 연구 질문을 "두 모멘트 상한이 서로 다른 주변확률에서 언제 정확한가(일반 n, k)"로 바꿨다. 데모 자체는 그대로 유효하다. 새 결과는 [`notes/research_reassessment.md`](notes/research_reassessment.md)와 [`notes/proofs/exactness.md`](notes/proofs/exactness.md)에 있다.

자세한 내용과 근거 파일은 [`README.md`](README.md), [`notes/claims.md`](notes/claims.md), [`notes/proofs/theorem_AB.md`](notes/proofs/theorem_AB.md), [`results/regions/REGIONS.md`](results/regions/REGIONS.md)에 있다.

## 알려진 한계

- 최적화 코드와 검증기를 같은 AI 도구로 작성했다. 이를 보완하려고 다음 장치를 두었다.
  - 검증기 명세를 코드보다 먼저 쓰고 사람이 검토했다.
  - 검증기가 최적화 코드를 import하지 못하게 테스트로 강제했다.
  - 변조한 증서가 실패하는지 확인하는 음성 테스트를 두었다.
  - 별도 부동소수점 해법(HiGHS)과 교차확인했다.
- 조각 경계 교점표(`results/regions/JUNCTIONS.md`)에서 좌표는 정확하다. 하지만 목록이 빠짐없는지는 수치 표본으로 판정했다.
- 선행연구 검색 범위 안에서는 같은 결과를 찾지 못했다. 다만 인용 데이터베이스 전체를 확인하지는 못했으므로 신규성을 확정하지 않았다(`notes/literature.md`).
