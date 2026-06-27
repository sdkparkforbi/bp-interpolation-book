# aday-bp-pipeline (Claude skill)

설문 + 스마트워치로 혈압(SBP/DBP)을 **추정·예측**하는 파이프라인 스킬. **수준·위상·편차 분해**, 20모형 zoo, AR 정적/동적 예측, MAE+BHS 평가.

## 설치 (Claude Code 스킬로)

이 `skill/` 폴더를 받아 자신의 스킬 디렉터리에 둔다:

```
~/.claude/skills/aday-bp-pipeline/
  ├─ SKILL.md
  ├─ README.md
  └─ scripts/        (파이프라인 .py + 레퍼런스 .json)
```

`/aday-bp-pipeline` 으로 호출하거나, 관련 작업 시 자동 인식.

## 내용

- **SKILL.md** — 방법론, 파일 맵, 실행 순서, 핵심 결과
- **scripts/** — PART1 보간 · PART2 추정 · PART3 예측 · 그림·책·논문 빌더 · 선행연구 JSON

## 주의

환자 데이터는 민감정보라 **미포함**. 스크립트는 방법론 템플릿이며 경로(`C:/Temp/HYPT/...`)와 데이터를 자신 환경에 맞게 조정해야 한다.

라이브 책·논문: https://sdkparkforbi.github.io/bp-interpolation-book/
