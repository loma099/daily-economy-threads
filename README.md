# 무료 클라우드 경제 브리핑 — 설정 중

목표: PC 전원과 무관하게 매일 한국시간 07:00에 최신 자료를 검토한 PNG와 글을 Threads에 게시합니다.

현재 상태: 배포 전. GitHub 로그인, Threads 공식 API 권한, 무료 AI 프로젝트 연결 및 실제 실행 검증이 필요합니다. 기존 카카오톡 프로그램과 인증 파일은 이 폴더에 복사하지 않습니다.

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

Secrets: `GEMINI_API_KEY`, `THREADS_ACCESS_TOKEN` (장기 사용자 토큰).

Variables: `GEMINI_MODEL`(무료 지원 모델을 연결 시 확인), `THREADS_USER_ID`, `PUBLIC_IMAGE_BASE`, `ENABLE_DAILY`(시험 통과 후 `true`).

Threads 장기 토큰은 만료 전에 갱신해야 합니다. 이 준비 버전은 토큰을 저장소에 기록하지 않으며, 무기한 무인 토큰 갱신은 아직 연결되지 않았습니다. 갱신 경로 검증 전에는 완성된 상시 서비스로 활성화하지 않습니다.

## 검증·배포 순서

1. GitHub 로그인 후 전용 공개 저장소 생성. 이 폴더 내용만 업로드.
2. Threads 앱 생성 및 본인 계정 게시 권한 동의. 무료 AI 프로젝트 연결.
3. 공식·시장 자료 공급원 보강과 숫자 교차 확인을 검증. RSS만으로 최신 종가가 확인되지 않으면 수치를 채우지 않음.
4. `ENABLE_DAILY`를 비활성으로 두고 수동 제작 및 이미지 검토.
5. 본인 Threads에 1회 시험 게시, 게시물·영수증·원본 이미지 확인.
6. 토큰 갱신·중복 방지 확인 후 예약 활성화.

## 근거 문서

- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://ai.google.dev/gemini-api/docs/pricing
- https://www.postman.com/meta/threads/collection/dht3nzz/threads-api
