# 모아노트에 첫 메모 남기기

slug: guide-demo · mode: guide · age band: E · group: 1 · total: 3 min · version: 1 · written: 2026-10-20

## Outcome

By the end, each learner **can** create and save a memo in a phone note app and **has made** one saved memo of their own. Evidence: the saved memo appears in the list.

Prior knowledge assumed: none. Prerequisite check: the app is open on the phone.

Test fixture for `tools/guide.py`. 모아노트 is a fictional app (`app.html` in this folder).

## Segments

| id | min | beat | title | what happens (learner's view) | modalities | media | game | story / humour |
|---|---|---|---|---|---|---|---|---|
| S1 | 1 | try | 새 메모 열기 | taps the new-memo button | do · see | M1 | – | – |
| S2 | 1 | try | 제목 쓰기 | types a title | do · see | M2 | – | – |
| S3 | 1 | check | 저장하기 | saves and reads the confirmation | do · read | M3 | – | – |

### Segment detail

#### S1 새 메모 열기
- instruction: "오른쪽 아래의 [+ 새 메모] 버튼을 눌러 주세요."
- expected: "제목과 내용을 쓰는 화면이 열립니다."
- fast / slow / wrong: – / – / 버튼이 안 보이면 화면을 위로 밀어 보세요.

#### S2 제목 쓰기
- instruction: "제목 칸을 누르고 메모 제목을 적어 주세요."
- expected: "적은 제목이 제목 칸에 보입니다."
- fast / slow / wrong: 내용 칸도 채워 보세요. / – / –

#### S3 저장하기
- instruction: "[저장] 버튼을 눌러 주세요."
- expected: "초록색으로 \"저장했어요\" 안내가 나옵니다."
- fast / slow / wrong: – / – / 안내가 없으면 저장 버튼을 한 번 더 눌러 주세요.

## Media list

| id | type | segment | purpose (one line) | status |
|---|---|---|---|---|
| M1 | screenshot+highlights | S1 | where the new-memo button is | drafted |
| M2 | screenshot+highlights | S2 | which field takes the title | drafted |
| M3 | screenshot+highlights | S3 | the save button and the confirmation | drafted |
