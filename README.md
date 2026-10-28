# pairwise-bound

KAIST 「인공지능기반수학발견」 개인 Math Research 과제 저장소.

## 문제

X1, …, X5 ∈ {0,1}, P(X1=1)=P(X2=1)=p, P(X3=1)=P(X4=1)=P(X5=1)=q, 서로 다른 두 변수는 모두 독립(상호 독립은 가정하지 않음).

M(p,q) = max P(X1+X2+X3+X4+X5 ≥ 3), 0 ≤ p ≤ q ≤ 1

의 정확한 값과 이를 달성하는 결합분포를 구한다. 모든 최종 주장은 유리수 정확 계산과 독립 검증기로 확인한다.

## 설치

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,symbolic,plot]'
```

## 문서

- 계획: [`notes/PLAN.md`](notes/PLAN.md)
- 문제와 가정: [`notes/problem.md`](notes/problem.md)
- 주장 상태: [`notes/claims.md`](notes/claims.md)
- 연구일지: [`notes/journal.md`](notes/journal.md)
- AI 상호작용 기록: [`notes/ai_log.md`](notes/ai_log.md)
- 세션 인계: [`notes/HANDOFF.md`](notes/HANDOFF.md)
