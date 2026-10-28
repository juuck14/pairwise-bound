# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 다음 행동
1. 선행연구 원문 확인 (arXiv:2006.00516) → `notes/literature.md`
2. 1단계: `verifier/SPEC.md` → `verifier/verify.py` → 대표점 증서와 음성 테스트

## 확인된 사실
- (아직 "정확 계산 검증" 이상으로 승격된 주장 없음. `claims.md` 참조)

## 미해결 질문
- R–N 논문의 정리 번호·가정이 우리 문제(특히 p=q 단면)에 직접 적용되는지
- 쌍대 꼭짓점 21개 중 내부 활성 조각이 정확히 몇 개인지(격자 탐색으로는 11개)

## 실패한 접근
- (없음)

## 재현 명령
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,symbolic,plot]'
pytest
```

## 환경 상태
- 원격: `https://github.com/juuck14/pairwise-bound` (세션에 연결됨, push 가능)
- 네트워크: arxiv.org 허용됨. export.arxiv.org, 저자 홈페이지, SSRN, SIAM은 차단.
