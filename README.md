# 무료 클라우드 경제 브리핑 — 설정 중

목표: PC 전원과 무관하게 매일 한국시간 07:00에 최신 자료를 검토한 PNG와 글을 Threads에 게시합니다.

현재 상태: 설정 중. 전용 공개 저장소에 제작·검토·게시 모듈을 올렸고 Ubuntu 서버의 기본 검사를 통과했습니다. 무료 AI 키는 비공개 Secret에 저장했습니다. Threads 최소 권한 토큰 연결 및 전체 제작·게시 시험이 남아 있습니다. 예약 게시를 아직 활성화하지 않았습니다. 기존 카카오톡 프로그램과 인증 파일은 이 폴더에 복사하지 않습니다.

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

Variables: `GEMINI_MODEL`(무료 지원 목록과 제공 여부를 확인해 선택), `THREADS_USER_ID`(선택), `ENABLE_DAILY`(시험 통과 후 `true`). 신규 프로젝트에서 Gemini 2.5 Flash가 HTTP 404를 반환하는 것을 확인해 후보에서 제외했습니다. 2026-11-02 공식 가격표상 무료 등급을 지원하는 3.8 Flash 등만 허용합니다. 게시 계정은 lej0954로 검사합니다. 공개 PNG는 이 전용 저장소의 raw 주소를 사용합니다.

Threads 장기 토큰은 만료 전에 갱신해야 합니다. 게시 모듈은 주기적으로 갱신하고 암호화한 토큰만 전용 저장소에 저장하도록 작성했습니다. 평문 토큰은 Secret에만 둡니다. 이 경로의 실제 시험은 아직 완료되지 않았습니다. 만료·취소·갱신 실패 시 게시를 중단합니다.

## 검증·배포 순서

1. GitHub 로그인 후 전용 공개 저장소 생성. 이 폴더 내용만 업로드.
2. Threads 앱 생성 및 본인 계정 게시 권한 동의. 무료 AI 프로젝트 연결.
3. 공식·시장 자료 공급원 보강과 숫자 교차 확인을 검증. RSS만으로 최신 종가가 확인되지 않으면 수치를 채우지 않음.
4. `ENABLE_DAILY`를 비활성으로 두고 수동 제작 및 이미지 검토.
5. 본인 Threads에 1회 시험 게시, 게시물·영수증·원본 이미지 확인.
6. 토큰 갱신·중복 방지 확인 후 예약 활성화.

## 중복·실패 처리

게시 전 날짜별 컨테이너 ID를 영구 저장합니다. 이 기록이 있는데 완료 영수증이 없으면 불확실한 재전송을 중단합니다. 응답 유실로 게시 성공 여부가 모호한 경우에는 자동으로 같은 글을 다시 올리지 않습니다. 계정·출처·본문 대조·PNG 검사·공개 URL 확인 실패도 게시 중단 사유입니다. 실패는 GitHub Actions의 실패 알림 설정으로 확인할 수 있습니다.

원문 텍스트·초안·검토 자료는 단기 검사 artifact로만 남기며 공개 코드에 커밋하지 않습니다. 공개 게시 파일에는 PNG, 출처 링크·시각, 인증정보가 없는 게시 영수증만 포함됩니다.

## 근거 문서

- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://ai.google.dev/gemini-api/docs/pricing
- https://www.postman.com/meta/threads/collection/dht3nzz/threads-api
