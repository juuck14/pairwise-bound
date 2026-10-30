# 연구일지

각 항목: 날짜, 목적, 실행 명령, 환경, 입력, seed(해당 시), 결과, 실패 원인.
"탐색"으로 표시된 결과는 저장소 코드로 재현·검증되기 전까지 주장으로 쓰지 않는다.

---

## 2026-10-28 (세션 1)

### J1. 작업 환경 확인
- `/home/user`: 비어 있음. proposal·기존 연구 기록 없음 → 사용자 설명을 유일한 명세로 사용.
- Python 3.13.17. 초기 설치 패키지: numpy만.
- 네트워크(실패 원인 기록):
  - 초기: arxiv.org, export.arxiv.org, ar5iv, people.sutd.edu.sg, papers.ssrn.com, researchgate, repository.sutd.edu.sg → 프록시가 CONNECT 403 (정책 차단). 문헌은 검색 스니펫으로만 수집.
  - 사람이 설정 변경 후: arxiv.org → 200. export.arxiv.org는 여전히 403.
  - `gh` CLI 토큰 무효, GitHub MCP 연결 실패 → 저장소 생성 불가. 사람이 GitHub에 `juuck14/pairwise-bound`를 만든 뒤 세션에 연결.

### J2. 계획 단계 탐색 계산 (탐색, 파일 미저장)
- 방법: `python3 - <<'EOF' ... EOF` 형태의 일회성 스크립트. Fraction 가우스 소거로 12상태 LP의 C(12,6)=924개 기저를 전수 열거. 외부 패키지 없음, 난수 없음.
- 결과(탐색):
  - (p,q)=(2/5,3/5): 최댓값 61/75. 지지 (0,0):8/75, (0,1):2/25, (0,3):13/75, (1,2):12/25, (2,1):2/25, (2,2):2/25.
  - 쌍대 f(a,b) = a − a(a−1)/3 + b(b−1)/6 − ab/6, 12점에서 1[a+b≥3] 지배, 값 2p − 2p²/3 + q² − pq = 61/75.
  - 정칙 기저 764개, 쌍대 실행가능 꼭짓점 21개. 60×60 격자 내부(0<p<q<1)에서 유일 최소인 이차식 11개.
  - p=q 표본점 7개(1/10, 1/3, 1/2, 3/5, 7/10, 3/4, 4/5)에서 12상태 값 = 단변수 S 모형 값.
  - S의 평균·이차모멘트만 쓰는 완화: 107/125 (> 61/75).
  - 비대칭: M(2/5,3/5)=61/75, M(3/5,2/5)=19/25; M(1/5,1/2)=139/300, M(1/2,1/5)=97/300; M(1/10,9/10)=79/100, M(9/10,1/10)=7/25.
  - 12×6 제약행렬 rank = 6.
- 하위 에이전트(설계 검토)가 메모리에서 같은 계산을 다시 해 61/75, 쌍대 실행가능 기저 50개 / 꼭짓점 21개, 120² 격자에서도 11개를 보고. 경계식 M(0,q)=q² (q≤1/2), 1−3q+3q² (q≥1/2), M(p,1)=1도 보고(미검증).

### J3. 0단계 셋업
- 명령:
  - `python3 -m venv .venv && . .venv/bin/activate`
  - `pip install scipy pytest sympy matplotlib`
  - `pip freeze > requirements.lock`
- 설치 결과: numpy 2.5.4, scipy 1.18.1, sympy 1.14.0, matplotlib 3.11.2, pytest 9.2.0 (전체 목록은 `requirements.lock`).

### J4. 선행연구 원문 확인
- 명령 (작업 디렉터리 밖의 임시 폴더에 내려받아 텍스트로만 읽음):
  - `curl -sSL -o abs.html https://arxiv.org/abs/2006.00516`
  - `curl -sSL -o src.tar.gz https://arxiv.org/e-print/2006.00516`
  - `tar -xzf src.tar.gz`
- 결과:
  - 판본 v1(2020-05-31)–v6(2022-11-23) 확인. v6 소스 `PairwiseIndependence_V4.tex`를 읽음.
  - 정리 번호와 적용 여부는 `notes/literature.md`에 기록.
  - 결론: p=q 단면은 Theorem 4.1의 특수경우(재현). p<q의 2+3 구조에 직접 적용되는 tight 결과는 원문에 없음. Prop. 4.5는 n−1개 동일 구조라 해당 없음. Theorem 3.1 상한을 (2/5,3/5)에 손으로 대입하면 107/125로, 61/75보다 큼(코드 재검증 예정).
- 실패/제약: SIAM 출판본은 접근 차단으로 번호 대조 불가.

### J5. 1단계: 검증기 우선
- 작성: `verifier/SPEC.md`(먼저), `verifier/verify.py`(SPEC만 근거, stdlib 전용), `src/pwbound/{rational,model,cert}.py`, `tests/`.
- 대표점 증서: 계획 단계 탐색값(π, f)을 손으로 옮겨 `pwbound.cert.build_certificate`로 조립(테스트 픽스처).
- 명령: `pytest` → 43 passed.
- 결과:
  - 대표점 증서가 격리 하위 프로세스(`python -I verifier/verify.py`)에서 28개 검사 모두 PASS. → C1(61/75)을 "정확 계산 검증"으로 승격.
  - 음성 테스트(주변 깨기, 쌍 깨기, 커널 이동으로 음수 만들기, 비트 반전, p 변경, y0 증감, 2배 계수 오류, 값 1/10⁹ 차이, p>q, 형식 오류 다수)가 모두 지정한 코드로 FAIL.
- 실패/수정: 테스트에 적은 검사 개수를 29로 잘못 셈(실제 28). 검증기 문제가 아니라 테스트 산수 오류였고, 코드 목록 대조로 바꿈.
- 미해결: SPEC의 사람 검토는 아직 하지 않음(자율 진행 지시에 따라 진행).

### J6. 2단계: 정확 해법
- 작성: `src/pwbound/exact_lp.py`, `scripts/make_certificate.py`, `tests/test_exact.py`.
- 명령:
  - `python -m scripts.make_certificate --p 2/5 --q 3/5` → `M(2/5, 3/5) = 61/75`
  - `python -I verifier/verify.py results/certificates/p2_5-q3_5.json` → `VERDICT: PASS`
  - `pytest` → 79 passed
- 결과 (정확 계산, 결정적):
  - 해법이 고른 기저 {(0,0),(0,1),(0,3),(1,2),(2,1),(2,2)}. π와 y가 계획 단계 탐색값과 같음.
  - 정칙 기저 764개, 쌍대 실행가능 기저 50개, 서로 다른 쌍대 꼭짓점 21개. 기저 다중도는 19개가 1이고 나머지 둘이 6과 25(퇴화 꼭짓점).
  - 세 정확 경로(원·쌍대 기저, 쌍대 이차식 최솟값, 원문제 기저 최댓값)가 무작위 유리점 15곳에서 일치. 점 생성 seed=20261028, 분모 60, [0,1]² 전체.
  - 생성 증서 17개(무작위 10 + 경계·대각 7)가 검증기 PASS. p>q 점은 `--allow-outside-scope`로 검증.
- 수정: `scripts` import를 위해 pytest `pythonpath=["."]` 추가.

### J7. 3단계: 부동소수점 교차확인과 일관성 테스트
- 작성: `src/pwbound/float_lp.py`(HiGHS, 제약을 `model`과 공유하지 않고 새로 구성), `src/pwbound/univariate.py`(S∈{0..5} 이항모멘트 LP, 정확), `tests/test_crosscheck.py`.
- 명령: `pytest` → 353 passed (+ 비대칭 점 증서 1개 추가 후 test_exact 재실행 PASS).
- 결과:
  - HiGHS 32상태·12상태 값 = 정확값 (허용오차 1e-9). seed=7 무작위 유리점 12곳.
  - p=q: 12상태 정확값 = 완전 대칭 단변수 모형 값. p=k/97, k=0..97.
  - 두 모멘트 완화는 항상 상한(seed=11, 20점). 대표점에서 107/125 > 61/75.
  - 상식 범위: 곱분포 값 ≤ M ≤ min(1,(2p+3q)/3) (seed=13, 20점).
  - 비대칭: M(2/5,3/5)=61/75, M(3/5,2/5)=19/25. 두 점 모두 증서가 검증기 PASS.
  - 경계: M(0,q)=q² (q≤1/2), 1−3q+3q² (q≥1/2), q=k/60 61점. R–N Theorem 4.1(n=k=3)과 일치. M(p,1)=1, 61점.

### J8. 4단계: 데모
- 작성: `scripts/demo.py`, `src/pwbound/report.py`, `tests/test_demo.py`, `notes/proofs/reduction.md`, README 갱신.
- 명령: `time python -m scripts.demo` → 종료 코드 0, 28/28 PASS. 실측 실행 시간 0.84초(real), 이 컨테이너 기준.
- 명령: `pytest` → 356 passed (실측 4.5초).
- 출력 요약: M=61/75. 12상태 지지 6점, 32상태 지지 17점. f(a,b)=a−(1/3)a(a−1)+(1/6)b(b−1)−(1/6)ab. Q(p,q)=−(2/3)p²−pq+q²+2p. HiGHS 차이 ≤ 4.4e−16. 두 모멘트 상한 107/125.

### J9. 깨끗한 클론 재현 확인
- 명령: 임시 디렉터리에 `git clone` → `python3 -m venv .venv` → `pip install -e '.[dev,symbolic,plot]'` → `python -m scripts.demo` → `pytest`
- 결과: 데모 28/28 PASS, 356 passed. 데모가 다시 쓴 증서 파일이 커밋된 파일과 바이트 단위로 같음(`git status` 변경 없음).

### J10. 정리 A·B: 영역 분류
- 작성: `src/pwbound/{poly,trimin,parametric,region_cert}.py`, `scripts/{scan,classify,plot_regions}.py`, `verifier/SPEC.md` §8(region 모드, 코드보다 먼저), `verifier/verify.py` region 모드, `tests/test_regions.py`.
- 명령:
  - `python -m scripts.scan --n 120 --record` → `results/runs/scan-n120/` (탐색, 4.6초)
  - `python -m scripts.classify` → `results/regions/region_certificate.json`, `results/regions/REGIONS.md`, 검증기 54/54 PASS (약 10초)
  - `python -m scripts.plot_regions` → `results/regions/region_map.png` (그림은 예시이며 증거가 아님)
  - `pytest` → 373 passed (16.8초)
- 결과 (검증기 PASS = 정확 계산 검증):
  - 정리 A의 계산 전제를 검증기가 독립 재계산으로 확인: rank 6, 곱분포 항등식, 쌍대 꼭짓점 21개 재열거 일치.
  - 정리 B:
    - 0<p<q<1에서 내부 활성 조각은 정확히 11개(V02, V10, V11, V12, V14, V15, V16, V18, V19, V20, V21). 각 조각에 유리수 목격점이 있다.
    - 나머지 10개는 D 전체 지배 덮개를 가진다. 9개는 단일 지배자, V04는 4분할(V02, V10).
  - 영역 기술: 꼭짓점 k의 영역 = {b(p,q) ∈ cone(tight 열)} = facet 부등식들. 퇴화 꼭짓점은 V06(tight 7, 기저 6, facet 10)과 V16(tight 8, 기저 25, facet 16).
  - 두 영역 기술(이차식 최솟값 vs 원뿔 소속)이 25×25 격자의 모든 점에서 일치(테스트).
  - 대표점 (2/5,3/5)은 V12 조각의 내부 점이며, 목격점 탐색에서 V12의 첫 목격점으로 나왔다.
- 관찰(탐색 → 문서화 예정): V02 = (p²+6pq+3q²)/3은 비순서 SSS 상한 S₂/C(3,2)와 같고, V16 = 1 − S₁ + S₂.
- 실패/수정:
  - 격자 기반 목격점 탐색이 꼭짓점마다 반복돼 2분 이상 걸림 → 한 번의 순회로 바꿔 8초.
  - 그림 라벨이 배열 테두리 쪽으로 쏠림(거리 변환이 테두리를 경계로 보지 않음) → 마스크에 여백을 덧대 해결.
- 인식 정정: 계획 단계에서 퇴화 꼭짓점을 "M=1 조각"으로 짐작했으나 실제로는 V06과 V16이었다(V18 M=1은 비퇴화).

### J11. 문헌 대조와 정리 문서
- 작성: `src/pwbound/rn_bounds.py`, `tests/test_rn_bounds.py`, `notes/proofs/theorem_AB.md`.
- 결과:
  - R–N 닫힌꼴 = 모멘트 LP (D의 31×31 격자).
  - (0,1)에서 닫힌꼴 지수 식이 0/0 → LP 값으로 대체(퇴화 입력, 실패 원인 기록).
  - 탐색(40×40 격자): 내부 점에서 순서 기반 BP(+§3.2)가 tight한 점은 V02 213/213, V16 27/27, V18 81/81. 그 외 조각은 0. 동률 점 39개 중 25개에서 tight.
  - 정확 논증: 상한 = W(8개 쌍대점)의 최솟값. 그중 rank 6인 것은 V02, V16, V18뿐 → 따름정리 C.
  - 단변수 쌍대 꼭짓점 (0, 7/15, −2/15)의 12상태 상 = (3/5)V10 + (2/5)V11 (테스트로 확인).
- 명령: `pytest` (전체 결과는 J12)

### J12. 마무리 확인
- 데모가 입력 점이 속한 조각 이름도 출력하도록 변경. 대표점 → V12.
- 명령: `pytest` → 981 passed (18.6초)

### J13. 조각 지도 교점
- 작성: `scripts/junctions.py`, `tests/test_junctions.py`.
- 명령: `python -m scripts.junctions` (약 3.5분, sympy가 연립 이차방정식 약 400개를 풂) → `results/regions/JUNCTIONS.md`.
- 첫 시도 실패: 표본점이 D의 변 위에 떨어지면 변 위에서 동률인 조각들(p=0에서 q²로 같은 V01/V02/V12/V14/V15, 대각선에서 같은 V10/V11) 중 번호가 앞선 것이 잡혀 가짜 교점이 섞임 → 표본을 D의 엄격한 내부로 제한해 해결.
- 결과: D 꼭짓점 3개 + 교점 11개, 그중 네 조각이 만나는 점 6개. 무리수 좌표 3개(7/8−√33/8, 1−√6/3, 1−√3/3).
- `pytest tests/test_junctions.py` → 15 passed: 표의 조각들이 각 점에서 M을 정확히 달성.

### J14. 후속 문헌 검색
- 웹 검색 2회, arXiv 검색 3회(`https://arxiv.org/search/?query=...&order=-announced_date_first`), arXiv:2209.01587 초록 확인.
- 결과: 같은 결과를 다룬 후속 문헌을 찾지 못함(검색 범위 한정, `notes/literature.md` §4).
- 실패: arXiv 저자 페이지 URL(`/a/natarajan_k_1`) 404. 저자 ID를 몰라 검색 페이지로 대체.

### J15. 11/1 데모 제출 준비 (2026-10-29)
- `scripts/__init__.py`: 패키지를 설치하지 않은 상태에서도 `src/`를 경로에 넣어 `python -m scripts.demo`가 동작하게 함.
- pytest `pythonpath`에 `src` 추가.
- `requirements.txt`(최소 버전) 추가. 정확한 기록 환경은 `requirements.lock`.
- 다른 Python 버전 확인: 추적 파일만 복사한 디렉터리에서 `pip install -r requirements.txt`로 설치(editable 설치 없음) 후 데모와 `pytest` 실행.
  - Python 3.11.17 (numpy 2.4.6, scipy 1.17.1, sympy 1.14.0): 데모 28/28 PASS, 996 passed (25.2초)
  - Python 3.12.3 (numpy 2.5.4, scipy 1.18.1, sympy 1.14.0): 데모 28/28 PASS, 996 passed (16.3초)
  - Python 3.13.17 (기록 환경): 996 passed (25.3초)
  - 첫 시도 실패: pytest가 설치되지 않은 `pwbound`를 찾지 못함 → `pythonpath`에 `src` 추가로 해결.
- `results/demo_output.txt`: 대표 사례 데모 출력 저장. 부동소수점 차이 줄을 뺀 나머지가 현재 출력과 같은지 테스트로 확인.
- `SUBMISSION.md`: 실행 방법, 출력 해설, 검사 28개 내역, 소요 시간, 결과 요약, 한계.

### J16. 발표 내용 초안과 보강 확인 (2026-10-29)
- 작성:
  - `notes/presentation_content.md`: 슬라이드별 핵심 메시지, 내용, 시각 자료, 근거, 상태. 슬라이드 자체는 만들지 않음(사람 지시).
  - `scripts/plot_slice.py` → `results/regions/slice_q3_5.png`: q=3/5 단면에서 정확값, 기존 최선 상한, 상호 독립 값을 비교.
- 새로 확인한 것:
  - q=3/5 단면에서 순서 기반 상한 = 비순서 상한(p=(3/5)·k/60).
  - 조각 경계는 p=(√21−3)/10, 1/5, 1−√7/5 (sympy).
  - 1/5<p<3/5에서는 상한을 이루는 8개 이차식 어느 것도 M과 만나지 않음(sympy, 정확) → C13.
  - M=1 영역의 특징 q=1 또는 (q ≥ 3/2−p, q ≥ 1−p/3) → C12. V18 facet에서 유도하고 60분할 격자로 확인.
  - (탐색) 60분할 격자에서 기존 상한과 M의 차이 최대점은 (1/10,5/6): 389/450 vs 41/60 → C14.
  - 대표점의 상호 독립 값 1683/3125.
- 내용 초안 작성 후 자체 대조에서 고친 것:
  - M=1 조건에서 q=1 경우가 빠져 있었음.
  - 따름정리 C 요약에서 "내부가 없는 예외 집합 제외" 단서가 빠져 있었음.
  - `SUBMISSION.md`의 검사 28개 내역 산수 오류.
- 명령: `pytest` → 1000 passed. Python 3.11.17 (25.2초), 3.12.3 (21.5초), 3.13.17 (18.2초).

### J17. 제출 태그 시도 (2026-10-29)
- 명령: `git tag -a demo-v1` → `git push origin demo-v1`
- 실패: `send-pack: unexpected disconnect while reading sideband packet`.
  - 2·4·8·16초 간격 재시도와 작업 프로세스 재시작 뒤 재시도에서 모두 같은 오류가 났다.
  - 같은 시점의 브랜치 push(`main`)는 정상이었고 저장소 push 권한 점검도 정상이었다. 그래서 이 세션의 git 프록시가 태그 push를 받지 않는 것으로 판단했다(원인 미확정).
- 조치: 로컬 태그를 삭제했다. 제출 기준은 `main`의 최신 커밋으로 하고, 태그는 필요하면 사람이 GitHub에서 만든다.

### J18. 따름정리 C(claims C9) 정정 (2026-10-29)
- 계기: 사람이 (p,q)=(1/7,4/7)에서 M=24/49, 순서 기반 BP(강화판)=24/49, SSS(강화판)=73/147, Chebyshev(강화판)=48/97을 제시하고 C9 재점검을 요구했다.
- 재계산: 저장소 코드와 손계산(`notes/research_reassessment.md` §2)이 모두 네 값과 일치했다. 따라서 "SSS·Chebyshev도 BP형과 같은 집합에서 tight"라는 이전 서술은 틀렸다.
- 원인: 원래 증명은 OBP의 tight 집합만 다뤘다. SSS·Chebyshev ≥ OBP에서는 포함 관계(⊆)만 나오는데 등호로 썼다.
- 정정: BP형 R_V02 ∪ R_V16 ∪ R_V18 ∪ Z, SSS형 R_V02 ∪ R_V18 ∪ Z′, Chebyshev형 R_V18 ∪ Z″. 증명(ii)(iii)을 추가했다.
- 테스트 추가(`tests/test_rn_bounds.py`): 네 값, 11개 목격점에서의 판정, SSS 다항식 항과 Chebyshev 유리함수 항이 Q_V02·Q_V16과 항등적으로 같지 않음(sympy).
- 수정한 문서: `notes/proofs/theorem_AB.md`, `notes/claims.md`, `README.md`, `SUBMISSION.md`, `notes/literature.md`, `notes/presentation_content.md`.

### J19. 연구 재평가와 새 질문: BP는 언제 정확한가 (2026-10-29)
- 계기: 사람이 "기존 방법을 작은 사례에 적용한 전수계산에 그치는가"라는 우려의 독립 평가와 보완을 요청했다(`notes/research_reassessment.md`).
- 문헌:
  - R–N v6 소스(이전 세션 사본)에서 §1–5를 다시 읽었다. Example 3.2가 tight 사례를 수치로만 보고한다는 점, §5 열린 문제 두 개를 확인했다.
  - arXiv 검색 7회(검색어는 reassessment §3.2), 초록 확인 7편, 2209.08563 소스 일부.
  - 실패: INFORMS, ScienceDirect, JSTOR, RUTCOR, Semantic Scholar, Crossref, OpenAlex가 모두 `CONNECT tunnel failed, response 403`.
- 탐색 스크립트는 처음에 임시 폴더에서 썼다. 문서에 인용한 것은 같은 시드로 `scripts/explore_exactness.py`에 옮겨 다시 돌렸다. 아래 수치는 옮긴 판의 출력이다(`results/runs/explore-exactness/output.txt`, 96초).
  - certainty-random: 2,250점, 불일치 0
  - certainty-boundary: 경계 안 1,425 일치, 바깥 655 일치, 바깥 155점은 값이 1 − O(1e-8)라 허용오차 안(이론상 < 1)
  - certainty-minimal: 최소점 215 모두 실현 가능, 바로 바깥 215 모두 불가능(임시판에서는 195/195)
  - regimes: "not exact" 판정 1,113건 모두 실제로 비정확. "open" 1,287건 중 1,207건 정확, 80건 비정확(E2–E4로 판정 못 함)
  - split: n=4 254/254 일치. n=5,6 비정확 663건 중 28건이 모든 2-분할 조건 통과
  - positivstellensatz: n=5,k=2 495점 중 86점, n=6,k=2 2,162점 중 168점, n=6,k=3 12점 중 5점이 부등식을 만족하지만 표현 불가
  - productform: 경계점 236개 모두 실패
  - scaled(쌍 = c·p_ip_j): 실현 가능한 494건에서 조건부 평균 조건과 확실성 법칙 존재가 모두 일치
  - twovalued: 5,267건 중 580건(11%) 구성 실패
  - k2: n=3에서 max 공식 184/184, n ≥ 4에서 단순 공식 둘 다 자주 틀림
  - decomp: 용량 조건 만족 849건 중 111건이 분해 불가
  - kernels n=8: 예외는 {0,s,8}(2≤s≤6)과 {0,1,7},{0,1,8},{0,7,8},{1,7,8}뿐
- 정확한 결과(분수):
  - `scripts/explain_rn_example.py` → `results/exactness/rn_example_3_2.md`: R–N Example 3.2의 24칸 판정(7.4초). 정확한 법칙은 HiGHS 지지에서 분수로 다시 풀어 `general.verify_law`로 확인.
  - E2·E2′ 불충분 반례 2개와 정확 Farkas 이차식(`tests/test_exactness.py`)
  - 2+3 조각 11개의 원인 판정. V15 목격점이 p + 2q = 2 위에 있어서 처음 예상(E3)과 달리 E4로 판정됨을 테스트 실패로 발견하고 기대값을 고쳤다.
- 그 밖의 탐색: Example 3.2에서 2-분할 집계 상한의 최솟값(모든 분할 2,047개)은 k=5 0.99623, k=6 0.90178, k=9 0.12896, k=10 0.07115, k=11 0.02493, k=12 0.00636이었다(임시 스크립트, 약 4초/k). R–N 순서 기반 상한보다 k=5,6에서만 작았다 → C24(탐색).
- 명령: `pytest` → 전체 통과(약 40초).

### J20. 두 값 환원(명제 C3)과 오차 하한(명제 G) (2026-10-29)
- 명제 C3: 두 값 주변확률의 최소점에서는 b-좌표가 0이면 S = k가 강제된다. 그래서 확실성 문제가 ω = P(모든 b = 1)을 공유하는 두 1차원 모멘트 문제로 줄어든다(교차 모멘트 조건은 자동).
  - `python -m scripts.explore_exactness twovalued-reduced` → 5,182/5,182 실현 가능.
  - 구간 겹침의 닫힌꼴 증명은 하지 못했다(다음 작업).
  - 임시 탐색(e22)에서 (W)와 (N)의 ω-구간이 항상 겹쳤다. 실현 불가능한 쪽이 한 번도 나오지 않았다.
- 명제 G: 경우 (b)의 쌍대 g(s) = s(n+k−s)/(kn)와, 층 0,k,n에서 0이 되는 F_j(x) = x_j(S−k) − S(S−k)/n로 BP − P̄ ≥ max|Δ_j|/κ(n,k)를 증명했다(κ(5,3)=12).
  - `... gap`: 최선 일차결합 하한은 (3/5,4/5)에서 실제 오차와 같았고, n=6 무작위 4점에서 69–83%였다. 명제 G 자체의 하한은 그 약 1/3이다.
- 테스트 추가: 정리 S의 법칙 정확 구성(k=2, n=5·k=3 Petersen), 정리 L(a)의 국소 안정성(부동소수점), 명제 G.
- 추가(J20): 두 값 경우 중 k ≥ β의 축소.
  - 임시 탐색(e24, 8,390점): (W)의 지지 제한 s_lo = max(0,k−α)는 한 번도 걸리지 않았다. 증명: k − α < (β−1)b이므로 k − α ≤ ⌈(β−1)b⌉ − 1 = i − 1이다.
  - 따라서 W_hi = R–N 정리 4.1의 P̄(β,β,b)이다. (N)은 ω ≥ ω_N := max_j (2jb − V)/(j(j+1))이다. 겹침 조건은 P̄(β,β,b) ≥ ω_N이고, 표본 최소 여유는 0.0092였다.
  - **실패한 단순화:** V를 a=b(실수 α)로 아래에서 눌러 β,b만의 부등식 P̄(β,β,b) ≥ max_j (2jb − β(1−b))/(j(j+1))로 만들면 거짓이다(격자 117,941점 중 7,717점 위반, 예 β=60, b=0.992). α가 정수(≥ 1)라는 조건이 V를 키우는 것이 본질이므로, 증명은 정수 α를 유지해야 한다.

### J21. 벗겨내기(peeling) 구성: k = 2 증명과 일반 k의 설계 환원 (2026-10-30)
- 계기: 사람이 "추측 C 증명 이어서 진행해"라고 요청했다.
- 출발점: 최소점에서는 최댓값 좌표 j가 0이면 S = k로 강제된다(J20). 그래서 법칙 안에 "정확히 k개"인 설계가 반드시 들어 있다.
  - 이를 정면으로 쓰는 분해 L = (1−s)D + sR을 시도했다. D는 k-설계, R은 최댓값 좌표가 모두 1이고 나머지는 쌍별 독립인 법칙이다.
  - k-설계의 행합 조건이 (s, z_A)를 하나로 정한다. 그 결과 남는 문제는 "D가 실현 가능한가"뿐이다.
- 임시 탐색(scratchpad e30–e39, 고정 시드):
  - e30: q-세계(Y = 1−X) 판본이다. 12개 (n, m=n−k, β) 족 720점에서 θ = 1−s의 근은 매번 하나였고, D는 매번 LP로 실현 가능했다.
  - e31: D가 B 전체를 포함하는 k-집합(q-세계에서는 N 안의 m-집합)에 질량을 두지 않는 변형은 240점 모두 불가능했다. β=2에서는 그 질량이 Π_BB = (b²−s)/(1−s) > 0으로 강제된다.
  - e33: "랭크 1 결손" k-설계(Π = ππᵀ − c wwᵀ)를 무작위로 만들었다. 쌍 확률이 음이 아니면 k ≥ 3에서 1,050점 모두 실현 가능했다. k=2의 1건 실패는 π≈0.999 경계의 수치 허용오차였다.
  - e34: k=2 구성을 n=5–12의 1,800점에서 확인했다. 모멘트 오차는 10⁻¹⁵ 수준이었고, s/b²의 최댓값은 0.989였다.
  - e35: k≥3의 LP 실패 2건을 조사했다. 둘 다 좌표 하나가 약 10⁻⁶인 경우로, 위반량 최소화 LP의 값이 ≈ 0(−10⁻⁷)이어서 수치 문제로 판정했다.
  - e36: q-세계에서 B-링크를 Sampford 설계로 고정했다. 7개 족 중 4개에서 나머지 N-부분이 실현 불가였다(실패 접근).
  - e37: 극단 표집 5종으로 n=6–10을 확인했다. 위반은 0이었다.
  - e38–e39: 두 값 최소점에서 D의 존재를 1차원 조건 (I)·(II)로 판정했다. 182,726점 모두 성립했다. 여유가 0인 경우는 k=1과 α=1뿐이고, 둘 다 항등식으로 성립한다.
- 증명한 것(`notes/proofs/exactness.md` §2.1):
  - 보조정리 R(최소점 환원), P1(곡선 f_s(y) = (1−y)(b−sy)의 성질), P2(Φ(b²) = (k−1)(1−b)/b ≥ 0이므로 근 s ∈ (0, b²]), P3(D의 2×2 표 네 칸이 모두 ≥ 0).
  - 핵심 부등식은 s ≤ b²일 때 y ≤ a/√s이다. 근거는 f_s(a/√s) − f_1(a) = a(1−√s)(1−b/√s) ≤ 0이다.
  - **정리 C4: k = 2에서 추측 C가 성립한다.** 결과적으로 추측 C는 k ∈ {1, 2, n−2, n−1, n}에서 확정되고, n ≤ 5는 전부 해결된다.
  - 명제 C5(일반 k → 추측 D)와 명제 C7(두 값 → 1차원 창 부등식)도 증명했다.
- 저장소 반영:
  - 코드 `general.py`: `certainty_condition`, `minimal_point_below`(정확), `peeling_y`, `peeling_parameters`(부동소수점 이분법), `peeling_design_moments`, `peeling_law_k2`, `two_valued_k2_instance`(정확 유리수 족: β=2, a=(2−b)/α).
  - 테스트 7개: 정확 6사례, sympy 항등식, 무작위 최소점, 두 값 창.
  - `python -m scripts.explore_exactness peeling`(553점, 12초)과 `peeling-twovalued`(182,726점, 117초)를 추가했다.
- 하지 못한 것:
  - k ≥ 3에서 D의 존재(추측 D)는 증명하지 못했다.
  - 두 값 창 부등식도 증명하지 못했다. 이것은 s의 2차방정식(u = b/s)과 정수 j에 대한 유한 개 부등식이므로, 다음 세션의 1순위로 둔다.

### J22. 두 값 주변확률의 확실성 판정 증명(정리 C8) (2026-10-30)
- 출발점: 명제 C7은 두 값 경우를 "Φ의 근 s가 창 [W_lo, min_j s_j] 안에 있다"로 줄였다.
- 단계와 근거(임시 탐색은 scratchpad e40–e53, 고정 시드):
  - e40: 창의 끝점에서 부호 조건(Φ(W_hi) ≥ 0, k<β일 때 Φ(W_lo) ≤ 0)을 확인했다. 137,055점 모두 성립했다.
  - 부호 전이(T1): Φ의 부호는 이차식 G(b/s)의 부호와 같다. G가 오목이므로 s* = b/u₊가 가장 작은 근이고, 창 조건은 G의 부호 조건이 된다(T2).
  - e41: 아래 끝 조건 G(b/W_lo)·(양수)가 완전히 인수분해되었다. 부호가 바로 정해진다(T5).
  - e44, e46: 위 끝을 "실수 α, a=b" 완화로 줄이는 시도는 거짓이었다. e44는 6,313,237건 중 40,887건, e46은 j ≤ k−2만 보아도 14,067,867건 중 2,997건 위반이었다. 걸리는 첨자에서는 e47에서 244,186점 중 2,574점(약 1%) 위반이었다. → 실패 접근으로 기록.
  - e45: j = k−1에서 H가 β(α−1)(1−b)²(β−k)(k−1)(m−k)²로 인수분해되었다. 정수 α ≥ 1이 바로 쓰이는 지점이다.
  - e47–e48: 걸리는 첨자 j*에서 H는 α에 대해 일차식이다. 기울기 Q₁ > 0이었고, α = k−j*에서 H가 완전히 인수분해되었다. 그런데 모든 허용 α가 k−j* 이상이다(L_B ≤ j*). 그래서 정수 조건이 "α ≥ k−j*" 하나로 처리된다.
  - e49–e51: 기울기를 Q₁ = K_A·A₁ + A₀로 분해했다. A₁ > 0이고, A₁ + A₀는 판별식이 음인 이차식을 쓴 양의 다항식 표현을 가진다.
  - e50: argmin_j s_j = ⌈(β−1)b⌉ − 1을 200,000점에서 확인했다. 증명은 s_j − s_{j+1}의 항등식으로 했다(T3).
  - e52: W_lo ≤ b²를 확인했다. 증명은 일차식의 끝점 확인이다.
  - e53: 사슬 전체를 56,993점에서 확인했다. 모두 성립했다.
- 저장소 반영:
  - `general.two_valued_peeling_s`
  - 테스트 3개: sympy 항등식 2개(부호 전이, 창 항등식 묶음), 부동소수점 사슬 1개
  - exactness §2.1 정리 C8, claims C29
- R–N 원문 확인: Prop. 4.5(`prop:tightnonid`, n−1개 동일 + 1)는 p ≤ 1/(n−1)에서 비자명 상한의 tightness만 다룬다. 확실성 경우는 포함하지 않는다.
- 남은 것: 세 값 이상에서의 추측 D(일반 k ≥ 3). 첫 사례는 n=6, k=3이다.
