# 세션 인계

_매 세션 종료 시 갱신한다. 첫 줄의 "다음 행동"이 바로 할 일이다._

## 현재 연구 목표 (2026-10-29부터)
쌍별 독립 Bernoulli 변수에서 두 모멘트(Boros–Prékopa, BP) 상한과 R–N 순서 기반 상한이 **언제 정확하고 왜 깨지는가**를 일반 n, k에서 밝힌다.
- 배경·후보 비교·선택 이유: `notes/research_reassessment.md`
- 증명: `notes/proofs/exactness.md`
- 주장 상태: `notes/claims.md` C15–C28
- 원래 2+3 문제의 결과(C1–C14)는 이 질문의 사례이자 검증 자료로 보존한다.

## 다음 행동
1. **추측 C(확실성 판정의 일반 충분성) 증명.**
   - 현재 상태(2026-10-30, J21):
     - k ∈ {1, 2, n−2, n−1, n}은 증명되었다(정리 C4 = k=2, 벗겨내기 구성).
     - 3 ≤ k ≤ n−3은 명제 C5로 **추측 D**(벗겨내기 설계 D의 존재 = 가중 그래프 Π의 분수 K_k-분해)에 환원되었다.
     - 첫 미해결 경우는 n=6, k=3이다.
   - 1순위: **두 값 주변확률의 창 부등식(명제 C7) 증명.**
     - 이것이 되면 두 값 주변확률 전체(모든 n, k)에서 추측 C가 정리가 된다.
     - 해야 할 일:
       - u = b/s는 2차방정식 b(α−1)u² − [b((n−k)(α−1)+k−β) − c]u + b(n−k)(k−β) = 0의 근이다. 여기서 c = (α−k+(β−1)b)((n−1)b−k)이다(J21 유도, 검산 사례 α=3, β=2, k=2, b=3/4 → u=11/6).
       - 이 근을 (II) Ψ_j(s) ≥ 0(L_B ≤ j ≤ U_B−1)과 (I)(k<β일 때 s 하한)에 넣어 증명한다.
     - 여유가 0인 경우는 α=1과 k=1뿐이고, 둘 다 항등식이다(`python -m scripts.explore_exactness peeling-twovalued`).
   - 2순위: **추측 D 일반.**
     - D의 공분산은 κ(diag ω − ωωᵀ)이고 κ = b²/s ≥ 1이다. 동일 주변확률이면 D는 SRS다.
     - 후보 경로:
       - (a) 분수 K_k-분해의 명시적 식(예: k=3에서 π·ω의 대칭 다항식) 찾기
       - (b) "SRS의 가중 일반화"로서 연속 시간 pipage(간선별 누적 분산 κω_lω_t를 맞추는 마팅게일) 구성
       - (c) n=6, k=3만 먼저: 3-설계 = 가중 K_6의 분수 삼각형 분해
     - 실패한 경로(J21, claims 실패 표): B-링크 Sampford 고정, κ배 범주형 공분산 족의 조건화 귀납, B 전체 포함 집합 배제.
   - 이전 경로(c·p_ip_j 족 귀납, 두 값 ω-구간 겹침 C3)는 벗겨내기로 대체했다. C3은 여전히 두 값 경우의 필요충분 환원으로 유효하다.
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
- C17: 추측 C (3 ≤ k ≤ n−3 미증명). C26(명제 C5): 추측 D로 환원. C27: 추측 D(553점 실현 가능, 탐색). C28(명제 C7): 두 값이면 1차원 창 부등식으로 환원(182,726점 성립, 탐색)

## 미해결 질문
- 추측 C의 일반 증명(3 ≤ k ≤ n−3, 첫 사례 n=6, k=3) = 추측 D
- 두 값 창 부등식(명제 C7)
- 경우 (c)(i ≥ 2)의 전역 필요충분조건
- (II)의 닫힌꼴 판정
- 일반 p에서 P̄ 계산의 복잡도(R–N §5(a))
- 원래 문제의 잔여: 교점 목록 완전성(C11), 예외 집합 Z의 정확한 기술, p>q 분류

## 실패한 접근 / 수정 이력
- 추측 C의 증명 경로 5개 실패 또는 미완(`claims.md` 실패 접근 표, reassessment §6). 벗겨내기 설계 D를 단순화하는 3개 시도 실패(J21)
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
