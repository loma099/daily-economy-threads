# 무료 클라우드 경제 브리핑 — 매일 자동 게시

목표: PC 전원과 무관하게 매일 한국시간 07:00에 최신 자료를 검토한 PNG와 글을 Threads에 게시합니다.

현재 상태: 2026-11-02 예약 활성화. PC를 끄거나 Codex를 종료해도 GitHub 서버에서 실행합니다. 첫 예약은 2026-11-03 한국시간 오전 6시 35분 준비 시작, 오전 7시 이후 게시입니다. Threads @lej0954의 기본 프로필·게시 두 권한 연결, 공식 수치·단위·중복 차단 테스트 12개, 내용 검토, PNG 검토, 공식 API 이미지 처리 시험을 통과했습니다. 기존 카카오톡 프로그램과 인증 파일은 이 저장소에 복사하지 않습니다.

## 실행 구조

공개 GitHub 저장소의 표준 Ubuntu Actions → 공개 RSS·공식 발표 수집 → 무료 등급 AI로 한국어 초안 및 별도 검토 → 한글 PNG 렌더링 → 이미지 검토 → 공개 이미지 주소 확인 → Threads 공식 API → 날짜별 영수증.

- 예약 실행은 UTC 21:35(한국 다음날 06:35)에 준비를 시작하고 07:00 이후 게시합니다. GitHub 대기열 때문에 늦을 수 있습니다. 정각 보장 상품이 아닙니다.
- 공개 저장소의 표준 GitHub-hosted Actions는 무료입니다. 유료 runner, 유료 AI·검색, 결제 계정은 사용하지 않습니다.
- AI는 결제가 연결되지 않은 무료 등급 프로젝트가 필요합니다. 프로그램은 API 키만으로 결제 상태를 검증할 수 없습니다. 무료 한도 초과 시 중단하며 다른 유료 모델로 전환하지 않습니다.
- 무료 정책은 서비스 제공자가 변경할 수 있으므로 영구 무료를 보장하지 않습니다.
- 공개되는 것은 프로그램·브리핑·출처·게시 영수증뿐입니다. 개인 파일, 카카오 인증정보는 업로드하지 않습니다.
- Threads 브라우저 로그인만으로는 서버 게시가 허용되지 않습니다. `threads_basic`, `threads_content_publish` 권한으로 별도 OAuth 연결이 필요합니다. 인증 만료·취소 시 다시 연결해야 합니다.
- 내용·이미지 검토, 공개 URL 확인 중 하나라도 실패하면 자동 게시를 중단합니다. AI 검토는 무오류 보장이 아닙니다.
- 토큰이나 비밀번호를 README, JSON, 명령행 인자, 채팅에 넣지 마세요. GitHub Actions Secrets에만 등록합니다.

## 연결할 값

Secrets: `GEMINI_API_KEY`, `THREADS_ACCESS_TOKEN` (장기 사용자 토큰), `TOKEN_ENCRYPTION_KEY` (Fernet 암호화 키).

예약 및 게시 조건은 `.github/workflows/daily.yml`에 활성화했습니다. 별도 `ENABLE_DAILY` 변수는 사용하지 않습니다. 본문 제작·검토는 Gemini 3.8 Flash, 이미지 검토는 Gemini 3.1 Flash-Lite를 요청하며, 제공 여부와 무료 허용 목록을 검사합니다. 예전 `GEMINI_MODEL` 저장소 변수는 사용하지 않습니다. 신규 프로젝트에서 Gemini 2.5 Flash가 HTTP 404를 반환하는 것을 확인해 후보에서 제외했습니다. 게시 계정은 lej0954로 검사합니다. 공개 PNG 주소는 날짜와 파일 해시를 포함해 캐시로 이전 이미지가 표시되는 것을 방지합니다.

Threads 장기 토큰은 만료 전에 갱신해야 합니다. 게시 모듈은 주기적으로 갱신하고 암호화한 토큰만 전용 저장소에 저장합니다. 평문 토큰은 Secret에만 둡니다. 실제 만료 주기는 아직 도래하지 않았으며, 만료·취소·갱신 실패 시 게시를 중단합니다.

## 실행과 중지

매일 예약은 별도 조작 없이 실행합니다. 수동 실행은 Actions → Daily economic briefing → Run workflow를 사용합니다. publish를 선택하지 않으면 이미지 처리만 시험하고 공개 게시하지 않습니다. 중지는 같은 워크플로 페이지 메뉴의 Disable workflow를 사용합니다.

Recheck today's reviewed image는 당일 2시간 이내, 원문·내용 검토가 통과한 자료의 이미지 배치를 수정할 때만 사용하는 복구 도구입니다. 자동 예약은 항상 당일 자료를 새로 수집합니다. 복구에 필요한 원문 근거가 artifact에 없으면 다시 수집해야 합니다.

공식 FRED 자료는 공개 지연이 있을 수 있습니다. 각 표의 관측일을 표시하며, 서로 다른 관측일의 지수를 같은 거래일 종가로 설명하지 않습니다. EIA 현물과 원유 선물, 연준 참고환율과 국내 마감환율을 구분합니다. 확인하지 못한 수치·일정은 확인 불가로 표시합니다.

검증 기록: [최소 권한 연결](https://github.com/loma099/daily-economy-threads/actions/runs/41373946437), [최종 PNG 및 서버 이미지 처리](https://github.com/loma099/daily-economy-threads/actions/runs/41393823787).

## 중복·실패 처리

게시 전 날짜별 컨테이너 ID를 영구 저장합니다. 이 기록이 있는데 완료 영수증이 없으면 불확실한 재전송을 중단합니다. 응답 유실로 게시 성공 여부가 모호한 경우에는 자동으로 같은 글을 다시 올리지 않습니다. 계정·출처·본문 대조·PNG 검사·공개 URL 확인 실패도 게시 중단 사유입니다. 실패는 GitHub Actions의 실패 알림 설정으로 확인할 수 있습니다.

원문 텍스트는 작업 서버에서 대조에만 사용합니다. 이후 검사 artifact에는 원문 본문·발췌·근거 인용을 제외한 검토 자료와 PNG만 내보내며 3일 보관합니다. 공개 파일에는 PNG, 원문 인용을 제외한 생성 초안, 출처 링크·시각, 인증정보가 없는 게시 영수증을 포함합니다. 초기 설정 중 생성한 이전 검사 artifact는 원래의 3일 보관 기간 이후 만료됩니다.

## 근거 문서

- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://ai.google.dev/gemini-api/docs/pricing
- https://www.postman.com/meta/threads/collection/dht3nzz/threads-api
