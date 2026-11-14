# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 현재 연구 목표 (2026-10-29부터)
쌍별 독립 Bernoulli 변수에서 두 모멘트(Boros–Prékopa, BP) 상한과 R–N 순서 기반 상한이 **언제 정확하고 왜 깨지는가**를 일반 n, k에서 밝힌다.
- 배경·후보 비교·선택 이유: `notes/research_reassessment.md`
- 증명: `notes/proofs/exactness.md`
- 주장 상태: `notes/claims.md` C15–C33
- 원래 2+3 문제의 결과(C1–C14)는 이 질문의 사례이자 검증 자료로 보존한다.

## 다음 행동
0. (사람) 11/1 제출은 날짜가 지났다. 제출 여부와 태그는 사람이 확인한다(J26, J17). 제출 기준 커밋은 a84c6d7이고, 그 뒤 결과(J27)는 제출물에 포함되지 않는다.
1. **추측 C(확실성 판정의 일반 충분성) 증명.**
   - 현재 상태(2026-11-14, J27):
     - **n ≤ 6 전부 증명(정리 C13).**
     - k ∈ {1, 2, n−2, n−1, n}(C2, C4), 두 값 주변확률(C8), 최소점 |A| ≤ 3(C11)도 증명되어 있다.
     - 도구는 **블록 함수 보조정리 C12′**이다. 크기 범위 상관 다면체(명제 C9)의 면 h가 A의 많아야 두 좌표 T′을 뺀 나머지에 대해 대칭이고, f(k−β, x_{T′}) ≥ 0이면 성립한다.
     - |A| = 4의 면은 정확 열거로 확인했다(`general.range_cor_facets`).
   - 1순위: **n = 7.** 남은 면은 블록 면이 아닌 것들이다.
     - |A| = 4, 범위 [0,3](k=3, β=3): 경로 면 x₂(1−x₀) + x₃(1−x₁) − x₂x₃ ≥ 0 (12개)
     - |A| = 4, 범위 [1,4](k=4, β=3): 그 여집합 (12개)
     - |A| = 5, 범위 [1,3](k=3, β=2): 경로 면 x₃ + x₄ − x₀x₃ − x₁x₄ − x₃x₄ ≥ 0, 5-순환형 Σx − Σ_{순환 변} x_ix_j − 1 ≥ 0
     - |A| = 5, 범위 [2,4](k=4, β=2): Σ_{i≠0}x_i − x₁x₂ − x₁x₃ − x₂x₄ − 1 ≥ 0과 5-순환형
     - 삼각 부등식은 C11 (나)의 항별 논법으로 이미 성립한다.
     - |A| = 5의 목록은 Qhull(부동소수점, e65)로만 얻었다. 증명에 쓰려면 정확 열거가 필요하다. 전수 부분집합 열거는 C(25,15)라 불가능하므로, 각 면의 접하는 꼭짓점 랭크 확인과 능선 인접(각 능선이 정확히 두 면에 속함) 확인을 쓰거나 cdd 같은 정확 도구를 쓴다.
   - 경로·순환 면의 후보 접근:
     - (a) 근의 방정식(Σ_A y = k − β + b/s)과 Σ_A a를 써서 면 값을 일부 좌표의 함수로 줄인다. 2+2 분할은 이 방법으로 한 쌍의 함수가 되었다.
     - (b) 블록 면 두 개의 합 + 항별로 증명되는 나머지로 쪼갠다. 단, 면은 다면체의 다른 면들의 양의 결합이 아니다. 따라서 이 모멘트 족의 특수 구조(y ≥ a, s y ≤ √s a 등)를 써야 한다.
     - (c) |T′| = 3의 원자별 단조성은 b ≥ 2s에서만 성립한다. s의 상한과 결합할 수 있는지 본다.
   - 2순위: 일반 |A|. 블록 면이 아닌 면 유형의 구조(경로, 순환)를 분류한다.
   - 참고: 두 값 증명(C8)에서는 정수 조건이 핵심이었다. 실수 완화를 쓰지 말 것. C12′의 (ii)에서는 같은 면이라도 D 밖(R 위)의 다항식 표현이 결과를 바꾼다(J27 e59).
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
- 새 결과 (일반 n, k):
  - C15: 조건부 평균 항등식, 단조성
  - C16: 확실성 필요조건과 k ∈ {1, 2, n−2, n−1, n}에서의 충분성(k=2는 정리 C4, 2026-10-30)
  - C18: 정확성의 필요조건 E2–E5
  - C19: 그 불충분성의 정확한 반례
  - C20: 정리 S(SSS 이차항 정확성의 필요충분조건, k=2 따름)
  - C21: 층 차원 분류와 국소 이분법
  - C22: R–N Example 3.2 24칸 설명
  - C23: 2+3 조각의 원인 설명
  - C25: 명제 G(경우 (b)에서 BP 오차의 하한, 이질성에 1차)
  - C34–C35: 블록 함수 보조정리 C12′, 정리 C13(n ≤ 6에서 추측 C)
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
