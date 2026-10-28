# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 다음 행동
1. 정리 A(유한 포락선) 증명 문서 + 쌍대 꼭짓점 21개 표 생성 + 검증기 region 모드(V 독립 재열거)
2. 정리 B: 내부 활성 조각별 목격점·매개변수 달성분포, 비활성 조각의 분할 지배 증명, 영역도
3. R–N Theorem 3.1 순서 기반 상한을 코드로 구현해 정확값과 비교(tight 영역 구분)

## 확인된 사실 (근거는 `claims.md`)
- C1: M(2/5,3/5)=61/75 — 독립 검증기 PASS
- C2: 32상태 ⇔ 12상태 축소(정리 R), 쌍대 대응(명제 D) — 증명됨
- C4: p↔q 비대칭, M(3/5,2/5)=19/25 — 정확 계산 검증
- C5, C6: p=q 단면 = R–N Thm 4.1, M(0,q), M(p,1)=1 — 정확 계산 검증 + 문헌
- C7: 두 모멘트 상한(=R–N 비순서 BP)은 대표점에서 107/125로 tight하지 않음
- 쌍대 꼭짓점: 정칙 기저 764개, 쌍대 실행가능 기저 50개, 서로 다른 꼭짓점 21개(퇴화 2개: 기저 6개, 25개)

## 미해결 질문
- 21개 이차식 중 0<p<q<1 내부에서 실제로 활성인 조각이 정확히 몇 개인가(격자 탐색으로는 11개)
- 각 조각의 경계(원뿔곡선)와 교점의 정확한 기술
- R–N 순서 기반 상한이 tight한 (p,q) 영역
- SIAM 출판본의 정리 번호가 arXiv v6과 같은지(접근 차단)
- `verifier/SPEC.md`의 사람 검토(아직 안 함)

## 실패한 접근
- (없음) 사소한 수정 이력은 journal J5, J6 참조

## 재현 명령
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,symbolic,plot]'
python -m scripts.demo
python -m scripts.make_certificate --p 2/5 --q 3/5
python -I verifier/verify.py results/certificates/p2_5-q3_5.json
pytest
```
- 무작위 테스트 seed: 20261028, 20261029, 7, 11, 13 (`tests/`에 고정)

## 환경 상태
- 원격: `https://github.com/juuck14/pairwise-bound` (main에 push됨)
- 네트워크: arxiv.org 허용. export.arxiv.org, SIAM, 저자 홈페이지, SSRN은 차단.
- 깨끗한 클론과 새 venv에서 데모·테스트 재현 확인됨(journal J9)
