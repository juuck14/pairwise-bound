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
