# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 다음 행동
1. (진행 중) 11/1 데모 제출 준비와 발표 내용 문서 작성 — 이 단계가 끝나면 이 항목을 갱신한다.
2. 완료: `verifier/SPEC.md` 사람 검토(2026-10-29). 모델/버전 칸은 사람 결정으로 제거.
3. 발표 자료 자체는 사람이 내용 문서를 검토한 뒤에 만든다.
4. (선택 확장) 교점 목록이 빠짐없는지 엄밀화(C11은 좌표·최소 달성만 정확). 따름정리 C의 Z 집합 정확 기술. p>q 영역 분류.
5. (선택 확장) R–N을 인용한 2023–2026 후속 문헌 확인(신규성 판단 보강). SIAM 출판본 번호 대조(네트워크 허용 필요).

## 확인된 사실 (근거는 `claims.md`)
- C1: M(2/5,3/5)=61/75. 독립 검증기 PASS. 이 점은 조각 V12 = 2p − 2p²/3 + q² − pq의 내부다.
- C2: 32상태 ⇔ 12상태 축소(정리 R), 쌍대 대응(명제 D). 증명됨.
- C3 (정리 A): [0,1]²에서 M = 21개 쌍대 꼭짓점 이차식의 최솟값. 컴퓨터 보조 증명.
- C8 (정리 B): D 내부 활성 조각은 정확히 11개. 영역은 facet 부등식, 달성분포는 다항식. 영역 증서 54/54 PASS.
- C9 (따름정리 C): R–N 두 모멘트·순서 기반 상한은 V02, V16, V18 조각(+ 내부 없는 집합)에서만 tight.
- C4–C7, C10: 비대칭, p=q 단면(R–N Thm 4.1 재현), 경계 p=0과 q=1, 두 모멘트 상한 비tight, s-only 쌍대.

## 미해결 질문
- 교점 목록이 빠짐없다는 엄밀한 증명 (C11: 좌표와 최소 달성은 정확, 목록 완전성과 인접은 수치 판정)
- 따름정리 C의 내부 없는 예외 집합 Z가 정확히 어떤 곡선 조각인지
- p>q 영역(연구 범위 밖)의 분류
- 2+3 구조를 일반 (m,n) 그룹과 임계값 k로 확장했을 때의 구조
- R–N 이후 문헌에 같은 결과가 있는지(신규성 최종 판단)

## 실패한 접근 / 수정 이력
- 꼭짓점별 목격점 탐색이 반복 계산으로 2분 이상 걸림 → 한 번의 격자 순회로 8초 (J10).
- 그림 라벨이 배열 테두리에 붙음 → 거리 변환에 여백을 덧대 해결 (J10).
- R–N BP 닫힌꼴이 (p,q)=(0,1)에서 0/0 → 같은 상한을 정의하는 모멘트 LP 값으로 대체 (J11).
- 계획 단계 짐작("퇴화 꼭짓점은 M=1 조각")이 틀림. 실제 퇴화는 V06, V16 (J10).

## 재현 명령
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev,symbolic,plot]'
python -m scripts.demo                                   # 대표 사례
python -m scripts.classify                               # 영역 증서 + REGIONS.md + 검증
python -I verifier/verify.py results/certificates/p2_5-q3_5.json
python -I verifier/verify.py results/regions/region_certificate.json
python -m scripts.plot_regions                           # 영역도
python -m scripts.junctions                              # 교점표 (약 3.5분)
pytest                                                   # 996 tests
```
- 무작위 테스트 seed: 20261028, 20261029, 7, 11, 13 (`tests/`에 고정)

## 환경 상태
- 원격: `https://github.com/juuck14/pairwise-bound` (main에 push)
- 네트워크: arxiv.org 허용. export.arxiv.org, SIAM, 저자 홈페이지, SSRN은 차단.
- Python 3.13.17, numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, matplotlib 3.11.2, pytest 9.2.0 (`requirements.lock`)
