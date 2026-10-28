# pairwise-bound

KAIST 「인공지능기반수학발견」 개인 Math Research 과제 저장소.

## 문제

X1, …, X5 ∈ {0,1}이고 다음을 가정한다.
- P(X1=1)=P(X2=1)=p
- P(X3=1)=P(X4=1)=P(X5=1)=q
- 서로 다른 두 변수는 모두 독립이다(상호 독립은 가정하지 않음).

이때 다음 값과 이를 달성하는 결합분포를 구한다.

M(p,q) = max P(X1+X2+X3+X4+X5 ≥ 3),  0 ≤ p ≤ q ≤ 1

모든 최종 주장은 유리수 정확 계산과, 최적화 코드와 분리된 독립 검증기로 확인한다.

## 빠른 시작

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,symbolic,plot]'
python -m scripts.demo                    # 대표 사례 p=2/5, q=3/5
python -m scripts.demo --p 1/5 --q 1/2    # 다른 유리수 입력
pytest                                    # 전체 테스트
```

데모는 다음을 출력한다(네트워크·LLM API 호출 없음).
- 정확한 최댓값
- 12상태 (A,B) 달성분포와 이를 복원한 32상태 분포
- 상한 증서(쌍대 다항식)와 그 값의 (p,q) 이차식
- HiGHS 부동소수점 교차확인
- 독립 검증기(`python -I verifier/verify.py`)의 28개 검사 결과

대표 사례 출력 요약:

```
M(p, q) = 61/75  ~= 0.8133333333
f(a, b) = a - (1/3)a(a-1) + (1/6)b(b-1) - (1/6)ab      # f >= 1[a+b>=3] on 12 points
E f(A, B) = Q(p, q) = -(2/3)p^2 - pq + q^2 + 2p = 61/75
28/28 checks passed
VERDICT: PASS
```

## 현재까지의 결과

상태 정의와 근거는 [`notes/claims.md`](notes/claims.md)에 있다.

| 주장 | 상태 |
|---|---|
| M(2/5,3/5) = 61/75 | 정확 계산 검증 (독립 검증기 PASS) |
| 32상태 LP와 12상태 (A,B) LP가 동치 (S₂×S₃ 대칭화) | 증명됨 ([`notes/proofs/reduction.md`](notes/proofs/reduction.md)) |
| M(p,q)는 21개 쌍대 꼭짓점 이차식의 최솟값 | 정확 계산 검증(표본점), 증명 작성 중 |
| p↔q 비대칭: M(3/5,2/5)=19/25 ≠ 61/75 | 정확 계산 검증 |
| p=q 단면 = Ramachandra–Natarajan Theorem 4.1 (재현) | 정확 계산 검증 + 문헌 |
| S의 두 모멘트만 쓰는 상한(107/125)은 대표점에서 tight하지 않음 | 정확 계산 검증 |

## 저장소 구조

| 경로 | 역할 |
|---|---|
| `src/pwbound/model.py` | 32·12상태 모형 정의, 원·쌍대 복원 (단일 정의 출처) |
| `src/pwbound/exact_lp.py` | 12상태 LP 기저 전수열거 (Fraction), 쌍대 꼭짓점 |
| `src/pwbound/float_lp.py` | HiGHS 32·12상태 LP (교차확인 전용, 제약을 독립적으로 구성) |
| `src/pwbound/univariate.py` | S의 이항모멘트 LP (p=q 대조, 두 모멘트 상한) |
| `src/pwbound/cert.py` | 증서 JSON 생성 |
| `verifier/SPEC.md`, `verifier/verify.py` | 독립 검증기 명세와 구현 (표준 라이브러리만) |
| `scripts/demo.py` | 한 명령 데모 |
| `scripts/make_certificate.py` | 임의 (p,q)의 증서 생성 |
| `results/certificates/` | 증서 JSON |
| `tests/` | 모형, 정확 해법, 교차확인, 검증기 음성 테스트, 검증기 독립성 |
| `notes/` | 계획, 문제 정의, 증명, 주장 상태, 문헌, 연구일지, AI 상호작용 기록, 인계 문서 |

## 문서

- 계획: [`notes/PLAN.md`](notes/PLAN.md)
- 문제와 가정: [`notes/problem.md`](notes/problem.md)
- 증명: [`notes/proofs/`](notes/proofs/)
- 주장 상태: [`notes/claims.md`](notes/claims.md)
- 선행연구: [`notes/literature.md`](notes/literature.md)
- 연구일지: [`notes/journal.md`](notes/journal.md)
- AI 상호작용 기록: [`notes/ai_log.md`](notes/ai_log.md)
- 세션 인계: [`notes/HANDOFF.md`](notes/HANDOFF.md)
