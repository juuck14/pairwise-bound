# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 현재 연구 목표 (2026-10-29부터)
쌍별 독립 Bernoulli 변수에서 두 모멘트(Boros–Prékopa, BP) 상한과 R–N 순서 기반 상한이 **언제 정확하고 왜 깨지는가**를 일반 n, k에서 밝힌다.
- 배경·후보 비교·선택 이유: `notes/research_reassessment.md`
- 증명: `notes/proofs/exactness.md`
- 주장 상태: `notes/claims.md` C15–C33
- 원래 2+3 문제의 결과(C1–C14)는 이 질문의 사례이자 검증 자료로 보존한다.

## 다음 행동
1. **추측 C(확실성 판정의 일반 충분성) 증명.**
   - 현재 상태(2026-10-30, J21–J23):
     - k ∈ {1, 2, n−2, n−1, n}은 정리 C4(k=2, 벗겨내기 구성)로 증명되었다.
     - **두 값 주변확률 전체**는 정리 C8로 증명되었다.
     - **최소점에서 |A| ≤ 3**(최댓값보다 작은 좌표가 많아야 셋)은 정리 C11로 증명되었다.
     - 나머지는 명제 C9로 "A 위의 크기 범위 법칙 μ_A의 존재"(추측 D)에 환원되었다. 그 1차원 B-개수 조건은 모든 최소점에서 성립한다(명제 C10).
     - 첫 미해결 경우는 n=6, k=3, β=2이고 A의 네 좌표가 두 값 이상인 경우다.
   - 1순위: **n=6, k=3을 끝내기.** 남은 것은 β=2, |A|=4, 범위 [1,3]에서 2+2 분할 면 −(U−1)(V−1) ≥ 0 하나다(exactness §2.2, J24–J25).
     - 모멘트 꼴: A = {i,l} ∪ {j,m}, δ_v = v_i+v_l−v_j−v_m에 대해 δ_a² + (1−s)(b²−s)/s ≥ s·δ_y²이다. 여기서 Σ_A a = 3−b, Σ_A y = 1+b/s이다.
     - 후보:
       - (a) y_s의 오목성과 증가성으로 |δ_y|를 δ_a와 (b,s)로 누른다. 같은 합에서는 퍼진 쌍이 y-합이 작다.
       - (b) 분할 면을 두 블록 현의 조합으로 쓰는 식을 찾는다(U−V의 현과 N의 현).
     - 수치: 최소 여유 7·10⁻⁵, b → 1(e57).
   - 그다음: |A| = 4의 다른 범위([0,3], [0,4], [1,4])에서 남는 부호 섞인 현(x₀+x₁+x₂−x₃, (x₀+x₁)−(x₂+x₃))을 처리한다. 그 뒤 일반 |A|(블록 현 보조정리 C12는 |T′| ≤ 2까지만 증명됨)로 간다.
   - 2순위: 일반 |A|. C10의 B-개수 조건은 모든 크기에서 성립한다. 따라서 "A 쪽의 범위 상관 다면체 면들이 항별 또는 B-개수 조건으로 귀결되는가"가 핵심 질문이다.
   - 참고: 두 값 증명(C8)에서는 정수 조건이 핵심이었다. 실수 완화를 쓰지 말 것.
2. 경우 (c)(지지 {i−1,i,k}, i ≥ 2)의 장애 분류: E2, E2′ 다음 단계인 매칭형 장애(C19의 n=5 반례)를 일반화한다. `python -m scripts.explore_exactness split`의 "split-ok but not exact" 28건이 시험 사례다.
3. 정리 S의 (II)(순위 1 가중 그래프의 분수 K_k-분해) 판정을 n=5, k=3(Petersen) 너머로 확장한다. `... decomp`의 용량-만족·분해-불가 111건이 시험 사례다.
4. (사람) `notes/proofs/exactness.md` 검토. 특히 보조정리 L1의 인용(Gottlieb–Kantor–Wilson), 정리 L(b)의 엄밀 상보성 가정, 정리 S의 (III).
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
- C17: 추측 C (|A| ≥ 4이고 세 값 이상, 3 ≤ k ≤ n−3 미증명). C32(정리 C11): |A| ≤ 3 증명. C30–C31: A로의 환원, B-개수 조건. C26(명제 C5): 추측 D로 환원. C27: 추측 D(553점 실현 가능, 탐색). C28(명제 C7) + **C29(정리 C8): 두 값 주변확률은 증명됨**

## 미해결 질문
- 추측 C의 일반 증명(|A| ≥ 4이고 세 값 이상, 3 ≤ k ≤ n−3, 첫 사례 n=6, k=3, β=2) = 추측 D
- 경우 (c)(i ≥ 2)의 전역 필요충분조건
- (II)의 닫힌꼴 판정
- 일반 p에서 P̄ 계산의 복잡도(R–N §5(a))
- 원래 문제의 잔여: 교점 목록 완전성(C11), 예외 집합 Z의 정확한 기술, p>q 분류

## 실패한 접근 / 수정 이력
- 추측 C의 증명 경로 5개 실패 또는 미완(`claims.md` 실패 접근 표, reassessment §6). 벗겨내기 설계 D를 단순화하는 3개 시도 실패(J21). 두 값 창 부등식의 실수 α 완화는 거짓(J22)
- C9 오류: 포함 관계를 등호로 씀 → 정정(J18)
- V15 목격점을 E3로 예상했으나 p+2q=2 위에 있어 E4 → 테스트 기대값 수정(J19)
- 이전 이력: 목격점 탐색 속도(J10), 그림 라벨(J10), R–N 닫힌꼴 0/0(J11), 퇴화 꼭짓점 짐작(J10)

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
