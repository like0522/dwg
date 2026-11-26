---
name: metal-fabrication-qa
description: >-
  제관, 용접 및 기계 후가공(5면가공기/보링 등) 도면 전수 검도 및 단품가공도(CP) 검증·작도 통합 스킬.
  조립도(상부)와 단품도(하부) 간의 누락 단품, 형강 마구리 공제 연산, 스티프너/보강리브 수량 오류,
  가공기호(6.3, 25 등) 기반 소재 여유 치수(Blank Allowance), DRC/DFM/DFA/DXF 사전 검증,
  AutoCAD COM+LISP 고속 덤프, AI_MOD_BOX 시각적 수정 하이라이트 및 병렬 시트 검도를 일괄 수행할 때 사용합니다.
---

# 제관·용접·후가공 도면 통합 검도 (Metal Fabrication & CAD Inspection QA v3.1)

제관·용접 구조물 및 기계 후가공 도면(상부 조립도 ↔ 하부 단품 제작도/절단 BOM)을 **Antigravity 병렬 워크플로우·멀티모달 비전·AutoCAD COM+LISP** 기반으로 전수 검도하고, 수정 LISP(`AI_MOD_BOX`) 및 AI 단품도(`AI_CP`)를 자동 생성하는 통합 엔지니어링 스킬입니다.

### 상세 레퍼런스 및 스크립트 (필요 시 로드)
* **기하 DRC, Readback 검증 및 제도 표준**: [references/drc_and_standards.md](./references/drc_and_standards.md)
* **DFM/DFA 가공·조립성 및 DXF 절단 사전 검증**: [references/dfm_dfa_and_dxf.md](./references/dfm_dfa_and_dxf.md)
* **고속 CAD 엔티티 덤프 리습**: [scripts/dump_full_drawing.lsp](./scripts/dump_full_drawing.lsp)

---

## 1. 제관 및 선/후가공 대원칙 (Engineering Rules)

### 1.1 후가공 원칙 (Post-Machining Default)
- 모든 제관·용접 구조물의 정밀 가공면, 탭(TAP), 리머/보링 홀은 **용접 완료 후 후가공(5면가공기, 보링기 등)을 원칙**으로 합니다.
- 후가공 대상 가공 유형:
  | 가공 유형 | 대표 주석 키워드 | 설명 |
  |---|---|---|
  | 탭(TAP) 가공 | `M16x2 DP 46`, `M24x3 DP 60` | 볼트 체결용 암나사 |
  | 관통홀 | `Ø27 THRU`, `Ø22 관통` | 볼트/핀 관통 구멍 |
  | 보링 가공 | `Ø98 양면가공`, `Ø120H7`, `내경-Ø40` | 베어링/부시/파이프 삽입면 |
  | 키홈 가공 | `KEY WAY 28x7`, `KEY 25x14` | 축-허브 결합용 |
  | 평면 가공 | `양면가공`, `FACE MILLING`, `6.3`, `25` | 접합면 평탄도 확보 |
  | 체인 커버 | `CHAIN COVER` | 커버 볼트 패턴 가공 |

### 1.2 후가공 소재 여유 치수 (Blank Allowance)
- 후가공이 들어가는 단품은 단품도 및 BOM 발주 치수에 **가공 여유를 포함한 원자재 소재 치수**로 등록해야 합니다.
- 표면 거칠기 기호(`6.3`, `25` 등, `기호(SK)` 레이어)가 표기된 면은 `Quote Ekosystem` 레이어 실측치 및 `치수(SK)` 완성 치수를 대조하여 두께(t)와 폭/길이 방향 가공 여유를 함께 검증합니다.
- **표준 가공 여유 테이블**:

  | 완성 치수 (t) | 가공 방향 | Blank 여유 | 발주 치수 (t) | 비고 |
  |---|---|---|---|---|
  | ≤ 30mm | 한쪽 면 | +1~6mm | 완성t + 4mm (표준 규격판) | 소형 블록 (예: `16T → 22T`, `24T → 25T`) |
  | 31~60mm | 한쪽 면 | +4~5mm | 완성t + 4mm | **기본 적용** (예: `46T → 50T`) |
  | 31~60mm | 양면 | +8~10mm | 완성t + 8mm | 양면 가공 |
  | 61~100mm | 한쪽 면 | +5~6mm | 완성t + 5mm | 중형 블록 |
  | > 100mm | 한쪽 면 | +6~8mm | 완성t + 6mm | 대형·특수 |
  | 폭 / 길이 방향 | 편측/양측 밀링 | +5~7mm / 양측 +2.5mm | 실측 + 5~7mm | 단가공 시 두께는 정치수 유지 |

  > **실무 예시**: 조립도 완성 두께 `46t` + `4-M16x2 DP 46` 탭 가공 블록(`46x250x280`)인 경우,
  > 단품도에는 **`50Tx250x280-1EA`**(가공 후 `46t`)로 작성되어야 합니다.

### 1.3 선가공 예외 원칙 (Pre-Machining Only Where Inaccessible)
- 용접 조립 후 가공 공구(스핀들/홀더)가 진입할 수 없거나 구조물과 간섭이 발생하는 협소한 내부 부위만 **선가공(Pre-Machining) 후 부착** 대상으로 분류합니다.
- 판단 기준: 공구 진입 경로(Spindle Clearance) 미확보 내부 포켓 / 용접 열변형 보정 불가 고정밀 조립면(IT7 이상) / 열처리(SR) 후 가공 불가 위치.

---

## 2. Antigravity 최신 검도 아키텍처 (듀얼 트랙 + 병렬 워크플로우)

과거의 순차적 단일 콘솔 실행 대신, **Antigravity의 병렬 서브에이전트(`run_workflow` / `invoke_subagent`), 멀티모달 비전(`read_file`), 대화형 UI(`generative_ui`)**를 결합하여 검도 속도와 정확도를 극대화합니다.

### 2.1 트랙 A: AutoCAD COM + AutoLISP 실시간 검도 및 수정 작도
AutoCAD가 실행 중이거나 수만 개의 엔티티가 포함된 경우 **COM ReadOnly 오픈 + AutoLISP `(ssget "X")` 고속 덤프**로 ~1초 내에 전수 데이터를 추출합니다.

1. **COM 연결 및 ReadOnly 오픈**: `win32com.client.Dispatch("AutoCAD.Application")` → `acad.Documents.Open(dwg_path, True)`
2. **LISP 고속 덤프 (`scripts/dump_full_drawing.lsp`)**: 도면 폴더에 `lisp_dump.txt` 생성 (`TEXT, MTEXT, DIMENSION, LINE, CIRCLE, ARC, LWPOLYLINE` 일괄 추출).
3. **Polyline 정점 역산**: 하부 단품 영역(`Y < -70000`) `AcDbPolyline` `Coordinates`로 실제 외형(`dx × dy`) 및 홀 중심/직경(`CIRCLE`) 역산.
4. **Readback & 시각적 변경 하이라이트 (`AI_MOD_BOX`)**:
   - AutoLISP 수정·추가 시 변경된 모든 객체 외곽에 **초록색(`Color = 3`) 닫힌 `LWPOLYLINE` 박스**(`AI_MOD_BOX` 레이어)를 작도하고, 일괄 삭제 명령 **`ClearModBoxes`**를 함께 제공합니다.
   - AI 단품도(AI-CP) 생성 시에는 전용 레이어 **`AI_CP`**에 기존 단품도 하단으로 배치하고, 일괄 정리 명령 **`ClearAICP`**를 함께 제공합니다.

### 2.2 트랙 B: 무인 DWG → DXF 변환 및 `.venv` 고속 분석
이미 구축된 `.venv`(`ezdxf 1.4.5` 포함)를 직접 호출하여 불필요한 가상환경 재생성 없이 즉시 실행합니다.

```powershell
.\.venv\Scripts\python dwg_pipeline.py "<대상도면.dwg>"
```
- **영역 분리**: 조립도(`Y > -75,000`) / 단품도(`Y < -70,000 ~ -104,000`) / 시트 클러스터링(`cluster_sheets.py`)

### 2.3 멀티 시트 병렬 검도 및 리포팅 (Antigravity Native)
1. **병렬 시트 팬아웃 (`run_workflow` / `invoke_subagent`)**: 2개 이상의 시트(예: 7개 시트)가 포함된 도면은 시트별 서브에이전트에 분할 할당해 동시 교차 검도 후 결과를 집계합니다.
2. **비전 + YOLO 하이브리드 판독**: 도면 이미지/PDF가 있는 경우 `read_file` 멀티모달 판독과 `detect_weld_symbols.py`(YOLO 15종)를 병행하여 용접 기호·모따기·표면거칠기 누락을 자동 적발합니다.
3. **구조화 리포트 (`generative_ui` / Artifact)**: 검도 완료 후 불일치 요약표·가공 여유 대조표·수정 LISP 로드 명령을 Markdown 아티팩트 또는 인터랙티브 대시보드로 제공합니다.

---

## 3. 통합 6대 교차 검도 매트릭스 (자동화 게이트 일원화)

기존의 중복 체크리스트를 제거하고, 모든 검도 항목을 **AI 자동 검증 게이트**와 **엔지니어 최종 사인오프**로 일원화했습니다.

| 검도 항목 | 검증 방법 (자동화 도구/로직) | 불합격 판정 기준 |
|---|---|---|
| **1. 헤더·시트·세트 일관성** | 파일명·상부(`PART NO.`, `PROJECT`) ↔ 하부 헤더 대조, `find_missing_parts.py` | 타 프로젝트 문구 잔존, 도번 시트 누락, `LH/RH` 대칭 누락, 1세트 vs 총수량 혼동 |
| **2. 단품 라벨 vs 실제 형상** | `check_missing_geometries.py` + Polyline 외형/홀 역산 (`총홀수 ÷ 홀/매 = 수량`) | 라벨만 있고 형상 0개, 복사 오류로 타이틀(`12tx...`)과 실제 외형/두께/홀 불일치 |
| **3. 형강 마구리 공제 연산** | 조립도 스팬 - 접합부 웹/플랜지 두께 공제 검증 (`2300-200-8=2092`, `700-9=691`) | 마구리 공제 누락 또는 상/하부 판두께(`3.5T` vs `4.5T`) 불일치 |
| **4. 가공 주석 & 여유 치수** | `audit_assembly_vs_parts.py` (`DP`, `THRU`, `KEY WAY`, `6.3`, `25`) + `Quote Ekosystem` 대조 | 가공 주석 대응 단품 누락, Blank Allowance(두께/폭/길이 여유) 미반영 |
| **5. 스티프너/보강리브 수량** | `count_stiffeners.py`, `count_95x175.py` (`개소 × 빔 수량 × 단/양면`) | BOM 기재 수량 ≠ 도면 실측 집계 수량 |
| **6. 기하 무결성 & 용접(DRC/DFM)** | `inspect_drawing.py` + `detect_weld_symbols.py` + `read_file` 비전 판독 | 치수 Override, 중복선(`OVERKILL`), `0.1mm` 미만 미소선분, 열린 윤곽선, 용접/선가공 주기 누락 |

### 엔지니어 최종 사인오프 (최소 육안 확인 3항목)
- [ ] **발주 사양 적합성**: 고객사 특수 요구(도장, NDT 비파괴검사 등급, 열처리/SR 여부)가 반영되었는가?
- [ ] **선가공 예외 판단**: 스핀들 간섭이나 협소 포켓 부위에 `PRE-MACHINING` 주기가 타당하게 지정되었는가?
- [ ] **AI 수정 박스(`AI_MOD_BOX`) 검토**: 초록색 하이라이트 영역 확인 후 `ClearModBoxes`로 정리하고 최종 저장했는가?

---

## 4. 스크립트 및 오픈소스 도구 실행 가이드

### 4.1 사내 검도 스크립트 참조
| 스크립트 | 용도 | 주요 입력 | 주요 출력 |
|---|---|---|---|
| `scripts/dump_full_drawing.lsp` | AutoCAD COM+LISP 고속 엔티티 덤프 | 활성 DWG | `lisp_dump.txt` (도면 폴더) |
| `dwg_pipeline.py` | DWG→DXF 무인 변환 | `.dwg` 파일 경로 | `.dxf` 파일 |
| `cluster_sheets.py` | 도곽 기반 Sheet 분리 | `.dxf` 파일 경로 | Sheet 목록(X범위) |
| `find_missing_parts.py` | 조립도↔단품도 도번 대조 | `.dxf` 파일 경로 | 누락 도번 리스트 |
| `check_missing_geometries.py` | 단품 라벨 vs 실제 형상 존재 확인 | `.dxf` 파일 경로 | 형상 누락 항목 |
| `audit_assembly_vs_parts.py` | 조립도 가공 주석/BOM → 단품도 교차 검증 | `.dxf` 파일 경로 | 누락/불일치 리스트 |
| `verify_specific_parts.py` | 특정 가공 블록 단품 존재 확인 | `.dxf`, 치수 조건 | 존재 여부 판정 |
| `compare_bom.py` | BOM 항목 간 수량/치수 비교 | `.dxf` 파일 경로 | 불일치 테이블 |
| `count_95x175.py` / `count_stiffeners.py` | 스티프너 좌표 및 총수량 카운팅 | `.dxf` 파일 경로 | X좌표별/총 수량 |
| `inspect_drawing.py` | 치수 override, 중복선, 미소선분 검출 | `.dxf` 파일 경로 | 콘솔 리포트 |
| `analyze_regions.py` | 도면 영역(조립/단품) 자동 구분 | `.dxf` 파일 경로 | 영역 경계 좌표 |
| `generate_shop_drawing.py` | 단품 가공도 자동 생성 | 형강 규격, 치수 | `.dxf` + `.lsp` |
| `detect_weld_symbols.py` | YOLO 기반 용접 기호 15종 자동 인식 | 도면 이미지(`.png`) | 바운딩박스/신뢰도 |

### 4.2 원샷 실행 예시 (`.venv` 기반)
```powershell
.\.venv\Scripts\python dwg_pipeline.py "신규도면.dwg"
.\.venv\Scripts\python cluster_sheets.py "신규도면.dxf"
.\.venv\Scripts\python find_missing_parts.py "신규도면.dxf"
.\.venv\Scripts\python check_missing_geometries.py "신규도면.dxf"
.\.venv\Scripts\python audit_assembly_vs_parts.py "신규도면.dxf"
.\.venv\Scripts\python count_stiffeners.py "신규도면.dxf"
.\.venv\Scripts\python inspect_drawing.py "신규도면.dxf"
```

### 4.3 설치 완료된 오픈소스 도구 (`tools/` & `.venv`)
| 프로젝트 | 설치 경로 | 핵심 기능 | 실행 방법 |
|---|---|---|---|
| `ezdxf` (v1.4.5) | `.venv` 전역 | DXF 2D/3D 파싱, BOM/치수/도곽 추출 | `.\.venv\Scripts\python <script.py>` |
| `weldCalloutIdentifier` | `tools/weldCalloutIdentifier` | YOLO 기반 용접 기호 15종 자동 인식 | `.\.venv\Scripts\python detect_weld_symbols.py <도면.png>` |
| `sw-drawing-qc` | `tools/sw-drawing-qc` | DXF/PDF 도면 품질 검사, ISO 2553/2768 | `skills/sw-drawing-qc*.md` 규칙 적용 |
| `ConstructDrawingAI` | `tools/ConstructDrawingAI` | 2D 기술 도면 구조화 및 수량 산출 | `.\.venv\Scripts\python tools/ConstructDrawingAI/backend/app.py` |
| `FreeCAD_SheetMetal` | `tools/FreeCAD_SheetMetal` | 판금 굽힘 전개(Unfold), K-factor 계산 | `.\.venv\Scripts\python tools/FreeCAD_SheetMetal/tools/calc-unfold.py` |

---

## 5. 용접 조인트 표준 및 DXF/AutoLISP 파싱 주의사항

### 5.1 제관 구조물 주요 용접 조인트 패턴
```
├─ H-Beam 웹 ↔ 플랜지    : 양쪽 필릿 연속 용접
├─ 스티프너 ↔ 웹          : 양쪽 필릿, 필요 시 완전 용입
├─ 가공 블록 ↔ 본체       : 완전 용입 그루브 (가공 정밀도 확보)
├─ 베이스 플레이트 ↔ 컬럼 : 완전 용입 또는 부분 용입 그루브
├─ 보강 거셋 ↔ 프레임     : 필릿 또는 부분 용입
└─ 앵커 볼트 ↔ 플레이트   : 전둘레 필릿
```

### 5.2 알려진 DXF / AutoLISP 파싱 주의사항
| 문제 | 원인 | 대응 |
|---|---|---|
| `POLYLINE` vs `LWPOLYLINE` | 구버전 DWG의 3D 폴리라인은 `get_points()` 없음 | `LWPOLYLINE`만 쿼리하거나 `vertices`/`Coordinates` 속성 사용 |
| MText 서식 코드 | `{\fArial;H200x200}` 같은 서식이 텍스트에 혼입 | 정규표현식으로 `{\...;}` 사전 제거 |
| CP949 인코딩 | 한글 레이어명/텍스트 깨짐 | `ezdxf.readfile(path, encoding='cp949')`, LISP는 `encoding='cp949'` 저장 |
| 좌표계 혼용 | UCS/WCS 혼용 시 좌표 오차 | `(trans pt 1 0)`으로 WCS 통일 (LISP), ezdxf는 OCS→WCS 변환 |
| 치수 텍스트 위조 | `dxf.text` / DXF group `1`에 override 문자열 존재 | 측정값(`42`)과 `text` 필드 비교하여 불일치 적발 |
| 전개도/도곽 스케일 혼동 | 전개도 자체를 축척 배율로 작도 시 CNC 절단 오류 | 형상·전개도는 항상 `1:1` 실측 작도, 외곽 양식(도곽)과 `DIMSCALE`만 배율 적용 |
| 헤드리스 콘솔 VLA 오류 | `accoreconsole.exe`에서 ActiveDocument `nil` 반환 | 레이어/도형은 `entmake` 우선 사용, VLA 호출은 `vl-catch-all-apply`로 방어 |

---

## 6. 누적 검도 지식 베이스 (Inspection Knowledge Log)

> 새로운 도면 검도 또는 현장 피드백이 발생할 때마다 본 섹션에 케이스 번호, 프로젝트명, 적발된 오류 패턴, 고객사별 가공 여유 기준을 누적 기록하여 검도 정확도를 지속적으로 고도화합니다.

### [Case 01] 2026-11-25 — 이스턴 메탈 UAE (`45801051` FRAME / `45801052` STAND)
* **적발된 주요 오류**:
  1. `[45801051 - 15번]` 타이틀 `12tx250x300-8EA` 오기입 → 실제 형상 및 View C 기준 **`25tx200x320-4EA (2-Ø27 THRU)`** 확인.
  2. `[45801052 - 4번]` 타이틀 `16tx160x627-10EA` 오기입 → 실제 형상 기준 **`16tx160x245-10EA`** 확인.
  3. `[45801052 헤더]` `PROJECT: 아콘 판넬 그리스` → **`이스턴 메탈 UAE`** 수정 필요.
  4. `[45801053 STAND]` 상부 도면 존재하나 하부 단품도 시트 미작성.
* **검증된 가공 여유 표준 패턴**:
  - **FRAME 8번**: 도면 `16T` 완성 → 단품 `22T` (`+6.0 mm` 두께 여유)
  - **FRAME 9번**: 단차 가공(`24T` 부위 여유 `0 mm`) → `25T` 원판 적용
  - **FRAME 11번**: 도면 `61.1 mm` 완성 → 단품 `67 mm` (`+5.9 mm` 폭 여유, `60T` 정치수)
  - **FRAME 12번**: 도면 `166.0 mm` 완성 → 단품 `171 mm` (`+5.0 mm` 폭 여유, `65T` 정치수)
  - **FRAME 13번**: 도면 `134.8 mm` 완성 → 단품 `140 mm` (`+5.2 mm` 폭 여유, `60T` 정치수)
  - **STAND 2번**: 폭 `300 → 305 mm` (양측 `+2.5 mm`), 길이 `5021 → 5027 mm` (좌측 `+6.0 mm`)
  - **STAND 3번**: 길이 `620 → 627 mm` (모따기 측 `+7.0 mm`)
  - **STAND 4번**: `245` 방향 가공 여유 포함 (`16T` 정치수)

### [Case 02] 2026-11-25 — 신성몰트텍 G70ME-C10.7 (`외형 2BLOCK-.dwg`, 7개 시트)
* **적발된 주요 오류 및 주의사항**:
  1. `[NO. 2 외형 1BLOCK]` 품번 **25번 누락** (`24`→`26`으로 건너뜀).
  2. `[NO. 3/4 스테이볼트홀 강관]` 단품도 내부 품목 수량은 **1세트 기준**임(미들 `×4EA`, END `×2EA` 총수량 산출 시 곱셈 누락 주의). 또한 상부 주석 `3.5T`가 하부 단품도에서 `4.5T`로 상향 적용됨(`700 - 9 = 691 mm`).
  3. `[NO. 5 실린더중자]` 11번(`1145` vs Poly `1147.6`), 12번(`1106` vs `1106.6`), 13번(`1065` vs `1065.6`) 소수점 절사 확인 및 36번 파이프(`Ø48.6×Ø38.8`)의 `내경-Ø40` 보링 가공 지시 확인.
  4. `[NO. 6 하형정반 / NO. 7 외형정반]` 품번 **4, 5, 7, 8, 9번 공백**, 상부 주석 `50x50x4.5T` vs 하부 `100x50x4.5` 불일치(실측 100×50 기준 일치), NO. 6 6번 `-4.5t 마구리` 텍스트 누락 및 마구리 캡 수량(`10EA`/`6EA` vs 각관 `7EA`/`5EA`) 확인 필요.

### [Case 03] 2026-11-26 — 대한중전기 Ø1200 가지관 전개 표준 (`가지관.dwg` / `GAJIGWAN_CP.lsp`)
* **정립된 제관·전개 검도 기준**:
  1. **새들 교차 기준**: 가지관 **내경**($\text{OD}_b/2 - t$)과 메인관 외경($\text{OD}_m/2$) 교차로 갭·내부 간섭 방지.
  2. **롤링 전개폭**: 판재 중립축 기준 $\pi \cdot (\text{OD}_b - t)$ 적용 여부 검산.
  3. **심(Seam) 분할 및 중심선**: 심 분할각($0^\circ, 22.5^\circ, 30^\circ, 45^\circ$ 등)에 따라 `CL` 중심선이 실제 곡선 최고점(Peak)·최저점(Valley)에 정확히 위치하는지 확인 (상세 기준: [dfm_dfa_and_dxf.md](./references/dfm_dfa_and_dxf.md)).

---

## 7. 버전 이력

| 버전 | 일시 | 내용 |
|---|---|---|
| v1.0 | 2025-11-25 | 초기 스킬 작성 (3단계 검증, 후가공 원칙) |
| v1.1 | 2025-11-25 | 5단계 검증 확장, Blank Allowance 테이블 추가 |
| v2.0 | 2026-11-25 | 스크립트 참조 테이블, 체크리스트, 용접 기호 규칙, 오픈소스 참조, DXF 주의사항 대폭 추가 |
| v2.1 | 2026-11-25 | 오픈소스 도구 5종 최신 설치 및 `.venv` 환경 구축, `detect_weld_symbols.py` 래퍼 연동 |
| v3.0 | 2026-11-26 | `cad-fabrication-inspection` + `metal-fabrication-qa` 통합 및 누적 검도 로그 병합 |
| v3.1 | 2026-11-26 | Antigravity 최신 기능(병렬 시트 워크플로우, 멀티모달 비전+YOLO, `generative_ui`, `.venv` 직접 실행) 반영 및 중복 체크항목 일원화 |
