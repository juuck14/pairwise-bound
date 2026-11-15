# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 현재 연구 목표 (2026-11-14 재설정)
**R–N(arXiv:2006.00516 v6) 결론 절의 열린 문제 (a): k ≥ 2에서 tight 상한 P̄(n,k,p)를 효율적으로 계산할 수 있는가?** 먼저 k = 2를 다룬다.
- 재평가와 선택 이유: `notes/reassessment_2026-11-14.md`. 1차 재평가 뒤에도 같은 흐름(사례 확장)이 반복된 원인과, 기여 판정 기준 G1–G4가 적혀 있다.
- 작업 가설 **H(k=2)**: 정렬된 주변확률을 연속인 g개 이하 묶음으로 나눈 집계 LP들의 최솟값이 P̄(n,2,p)와 같고, g는 n에 의존하지 않는다. 참이면 P̄(n,2,p)는 다항식 시간에 계산된다.
  - **g = 4판은 n = 8에서 정확한 증서로 반증되었다**(J28 e78). 그 점에서는 g = 5로 충분하다.
  - g가 유계인지는 모른다.
  - 코드: `pwbound.aggregation`. 근거: J28.
- 이전 질문("BP는 언제 정확한가", 추측 C)의 결과(`notes/proofs/exactness.md`, claims C15–C35)는 보존한다. 다만 사례 확장(C8–C13)은 더 진행하지 않는다.

## 규칙 (2026-11-14 추가)
- 어떤 결과든 "기여"라고 적기 전에 G1(일반성), G2(기존 결과를 대입하면 어디까지 나오는지와 새로 필요한 단계), G3(질문의 출처), G4(문헌 확인 범위)를 적는다. 하나라도 비면 "계산" 또는 "재적용"으로 분류한다.
- "다음 행동" 1순위를 사례 단위("n = 7을 끝내기")로 쓰지 않는다. 일반 진술 단위로 쓰고, 사례는 그 진술의 시험으로만 쓴다.
- "새 결과"라는 표기를 쓰지 않는다. 문헌을 원문으로 확인하지 못했으면 "선행연구 미확인"이라고 쓴다.

## 다음 행동
0. **(사람) 중간 정리 검토: `notes/k2_report.md`.** 2026-11-15에 사람이 "결과 정리"를 골랐다.
   - 이 문서를 제출·발표에 어떻게 쓸지 정한다.
   - 다음 연구 방향을 고른다(아래 1–3). AskUserQuestion에서 제시한 선택지는 다음과 같다: 난해성, 다항식 알고리즘, 근사.
1. (선택지) 덮개 LP Λ_f(곱 비용, |S|에만 의존하는 제약)의 다항식 해법 또는 난해성 환원. k2_report §5-1.
2. (선택지) 근사 상수.
   - k = 2: 최선 상수 ≈ 2.42와 BP 최악 비 ≥ 1.505.
   - 고정 k ≥ 3: 다항식 시간 상수배 근사. 구성적 하한이 수치상 3배 안쪽이다.
3. (선택지) K1 등호 영역의 원문제 구성.
- 규칙(위)은 그대로다. 단순 구조 가설은 이미 많이 깨졌다(k2_report §3). 새 가설은 n = 9–10 적대적 시험을 먼저 통과해야 기록한다.

## 이전 질문의 보류 항목 (진행하지 않음)
1. 추측 C의 n ≥ 7(경로·5-순환형 면). 면 열거에 의존하는 경로라 일반화되지 않는다(재평가 §1).
2. 경우 (c)(지지 {i−1,i,k}, i ≥ 2)의 장애 분류: E2, E2′ 다음 단계인 매칭형 장애(C19의 n=5 반례)를 일반화한다. `python -m scripts.explore_exactness split`의 "split-ok but not exact" 28건이 시험 사례다.
3. 정리 S의 (II)(순위 1 가중 그래프의 분수 K_k-분해) 판정을 n=5, k=3(Petersen) 너머로 확장한다. `... decomp`의 용량-만족·분해-불가 111건이 시험 사례다.
4. (사람) `notes/proofs/exactness.md` 검토.
   - 기존 항목: 보조정리 L1의 인용(Gottlieb–Kantor–Wilson), 정리 L(b)의 엄밀 상보성 가정, 정리 S의 (III).
   - 2026-10-30 새 증명: §2.1의 정리 C4·C8(보조정리 R, P1–P3, T1–T5), §2.2의 명제 C9·C10, 정리 C11, 보조정리 C12. 핵심 항등식은 sympy 테스트로 확인했지만, 논증의 흐름(특히 C10의 비교점 논법과 C12의 단조성)은 사람의 검토가 필요하다.
   - 2026-11-14 새 증명: §2.2의 보조정리 C12′, 정리 C13. 특히 C12′ (i)에서 비교점 D_c의 지지가 "크기 k인 집합"이라는 점과, 0이 된 좌표를 빼는 처리를 검토해야 한다.
5. (사람, 병행 가능) 발표 내용 `notes/presentation_content.md`는 이번 재평가로 중심 메시지가 바뀌었다. 슬라이드 방향은 사람이 정한다. 이것은 연구 진행을 막는 조건이 아니다.
6. 문헌: 네트워크 허용이 바뀌면 Boros–Prékopa 1989, Prékopa–Gao 2005, Mádi-Nagy–Prékopa 2004, Qiu–Ahmed–Dey 2016 원문에서 "일반 사건의 SSS·BP sharpness 조건"을 확인한다(신규성 판단 보강, reassessment §3.3).

## 확인된 사실 (근거는 `claims.md`)
- 원래 문제: C1–C14. M(2/5,3/5)=61/75, 정리 A·B(11개 조각), C12(M=1 영역; 이제 C16에서 증명됨).
- C9 정정(2026-10-29): BP형 tight = V02 ∪ V16 ∪ V18 ∪ Z, SSS형 = V02 ∪ V18 ∪ Z′, Chebyshev형 = V18 ∪ Z″.
- 이전 질문의 결과 (일반 n, k; 대부분 재적용·사례 확장으로 재분류됨, 재평가 §2):
  - C15: 조건부 평균 항등식, 단조성
  - C16: 확실성 필요조건과 k ∈ {1, 2, n−2, n−1, n}에서의 충분성(k=2는 정리 C4, 2026-10-30)
  - C18: 정확성의 필요조건 E2–E5
  - C19: 그 불충분성의 정확한 반례
  - C20: 정리 S(SSS 이차항 정확성의 필요충분조건, k=2 따름)
  - C21: 층 차원 분류와 국소 이분법
  - C22: R–N Example 3.2 24칸 설명
  - C23: 2+3 조각의 원인 설명
  - C25: 명제 G(경우 (b)에서 BP 오차의 하한, 이질성에 1차)
  - C34–C35: 블록 함수 보조정리 C12′, 정리 C13(n ≤ 6에서 추측 C; 사례 확장)
- C17: 추측 C (|A| ≥ 4이고 세 값 이상, 3 ≤ k ≤ n−3 미증명). C32(정리 C11): |A| ≤ 3 증명. C30–C31: A로의 환원, B-개수 조건. C26(명제 C5): 추측 D로 환원. C27: 추측 D(553점 실현 가능, 탐색). C28(명제 C7) + **C29(정리 C8): 두 값 주변확률은 증명됨**

## 미해결 질문
- 추측 C의 일반 증명(|A| ≥ 4이고 세 값 이상, 3 ≤ k ≤ n−3, n ≥ 7) = 추측 D. n = 7은 경로·5-순환형 면으로 줄었다
- 경우 (c)(i ≥ 2)의 전역 필요충분조건
- (II)의 닫힌꼴 판정
- 일반 p에서 P̄ 계산의 복잡도(R–N §5(a))
- 원래 문제의 잔여: 교점 목록 완전성(C11), 예외 집합 Z의 정확한 기술, p>q 분류

## 실패한 접근 / 수정 이력
- 추측 C의 증명 경로 5개 실패 또는 미완(`claims.md` 실패 접근 표, reassessment §6). 벗겨내기 설계 D를 단순화하는 3개 시도 실패(J21). 두 값 창 부등식의 실수 α 완화는 거짓(J22)
- C9 오류: 포함 관계를 등호로 씀 → 정정(J18)
- V15 목격점을 E3로 예상했으나 p+2q=2 위에 있어 E4 → 테스트 기대값 수정(J19)
- 이전 이력: 목격점 탐색 속도(J10), 그림 라벨(J10), R–N 닫힌꼴 0/0(J11), 퇴화 꼭짓점 짐작(J10)

## 임시 탐색 스크립트
- 2026-11-14 세션의 e58–e65도 scratchpad에만 있다. 재현이 필요한 것은 테스트(`test_a4_facets_exact_and_block_form`, `test_split_facet_*`)로 옮겼고, |A| = 5 면 목록(e65)은 J27에 기록만 했다.
- 이전 세션의 임시 탐색(e30–e57)은 scratchpad에만 있고 저장소에는 없다. 문서에 인용한 수치 가운데 재현이 필요한 것은 `scripts/explore_exactness.py`의 `peeling`, `peeling-twovalued`, `facets-a4`와 테스트로 옮겼다. 그 밖의 e-번호 수치(e40, e44–e57 등)는 J21–J25에 기록만 했고, 저장소에서 같은 명령으로 재현되지는 않는다.

## 재현 명령
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt                          # 또는 pip install -e '.[dev,symbolic,plot]'
python -m scripts.demo                                   # 11/1 데모 (대표 사례)
python -m scripts.classify                               # 2+3 영역 증서 + REGIONS.md + 검증
python -m scripts.explain_rn_example                     # R–N Example 3.2 설명 (약 8초)
python -m scripts.explore_exactness all                  # 탐색 실행 전체 (약 4분, 부동소수점)
python -I verifier/verify.py results/certificates/p2_5-q3_5.json
python -I verifier/verify.py results/regions/region_certificate.json
pytest                                                   # 전체 테스트 (약 40초)
```
- 무작위 테스트 seed: 20261028, 20261029, 7, 11, 13 (`tests/`에 고정), 탐색 seed는 `scripts/explore_exactness.py`

## 환경 상태
- 원격: `https://github.com/juuck14/pairwise-bound` (main에 push)
- 네트워크: arxiv.org 허용. INFORMS·ScienceDirect·JSTOR·RUTCOR·Semantic Scholar·Crossref·OpenAlex·SIAM은 차단(403).
- Python 3.13.17, numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, matplotlib 3.11.2, pytest 9.2.0 (`requirements.lock`)
