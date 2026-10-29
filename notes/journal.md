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
