---
name: metal-fabrication-qa
description: >-
  제관, 용접 및 기계 후가공(5면가공기/보링 등) 도면 전수 검도 및 단품가공도(CP) 검증·작도 통합 스킬.
  조립도(상부)와 단품도(하부) 간의 누락 단품, 형강 마구리 공제 연산, 스티프너/보강리브 수량 오류,
  가공기호(6.3, 25 등) 기반 소재 여유 치수(Blank Allowance), DRC/DFM/DFA/DXF 사전 검증,
  AutoCAD COM+LISP 고속 덤프 및 AI_MOD_BOX 시각적 수정 하이라이트를 일괄 수행할 때 사용합니다.
---

# 제관·용접·후가공 도면 통합 검도 (Metal Fabrication & CAD Inspection QA v3.0)

제관·용접 구조물 및 기계 후가공 도면(상부 조립도 ↔ 하부 단품 제작도/절단 BOM)을 분석·검도하고, 기하 무결성(DRC)·제조성(DFM)·조립성(DFA)·DXF 절단 사전 검증을 일괄 수행하여 오제작 및 발주 미스를 원천 차단하는 통합 엔지니어링 스킬입니다.

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
- 선가공 판단 기준:
  - 공구 진입 경로(Spindle Clearance)가 확보되지 않는 내부 포켓
  - 용접 열변형으로 치수 보정이 불가능한 고정밀 조립면 (IT7 이상)
  - 용접 후 열처리(SR 처리) 뒤에도 가공이 불가능한 위치

---

## 2. 듀얼 CAD/DXF 데이터 추출 및 작도 파이프라인

도면 환경과 목적에 따라 **트랙 A (AutoCAD COM + AutoLISP 실시간 검도/수정)** 또는 **트랙 B (DXF 무인 변환 + Python 일괄 분석)**를 선택하거나 병행합니다.

### 2.1 트랙 A: AutoCAD COM + AutoLISP 고속 덤프 및 수정 (실시간 도면 연동)
AutoCAD가 실행 중이거나 수만 개의 엔티티가 포함된 경우, Python COM 단일 루프 대신 **COM ReadOnly 오픈 + AutoLISP `(ssget "X")` 고속 덤프**를 결합하여 ~1초 내에 전수 데이터를 추출합니다.

1. **COM 연결 및 ReadOnly 오픈**: `win32com.client.Dispatch("AutoCAD.Application")` → `acad.Documents.Open(dwg_path, True)`
2. **LISP 고속 덤프 (`scripts/dump_full_drawing.lsp`)**: `doc.SendCommand`로 `TEXT, MTEXT, DIMENSION, LINE, CIRCLE, ARC, LWPOLYLINE` 일괄 추출.
3. **Polyline 정점(Vertices) 정밀 추출**: 하부 단품 영역(`Y < -70000`) `AcDbPolyline`의 `Coordinates` 배열로 단품 실제 외형(`dx × dy`) 및 홀 중심/직경(`CIRCLE`) 역산.
4. **Readback 검증 원칙**: 도면 수정·작도 명령 실행 후에는 반드시 핸들/좌표/텍스트를 재조회(Readback)하여 정상 반영 여부를 확인합니다.
5. **시각적 변경 하이라이트 (`AI_MOD_BOX`) 표준**:
   - AutoLISP 스크립트로 도면을 수정·추가할 때는 **변경/추가된 모든 객체 외곽에 초록색(`Color = 3`) 닫힌 `LWPOLYLINE` 박스**를 `AI_MOD_BOX` 레이어에 작도합니다.
   - 반드시 `AI_MOD_BOX` 레이어 객체만 일괄 삭제하는 **`ClearModBoxes` 명령**을 함께 제공합니다.
6. **AI 단품도(AI-CP) 자동 생성 원칙**:
   - 검도 결과를 바탕으로 AI가 직접 단품도(Cutting Plan)를 작도할 때는 사용자 원본 단품도와 겹치지 않도록 **전용 레이어(`AI_CP`)**에 기존 단품도 하단 영역으로 배치하고, 일괄 정리용 **`ClearAICP` 명령**을 함께 제공합니다.

### 2.2 트랙 B: 무인 DWG → DXF 고속 변환 및 영역 분리 (Python/ezdxf)
AutoCAD GUI를 띄우지 않고 `dwg_pipeline.py`를 통해 `accoreconsole.exe`로 무손실 DXF를 추출한 뒤 분석합니다.

```powershell
uv run --with ezdxf python dwg_pipeline.py "<대상도면.dwg>"
```

- **조립도 영역**: Y > -75,000 (일반적 상부 영역)
- **단품도 BOM/형상 영역**: Y < -70,000 ~ -104,000 (하부 영역)
- **도번(Sheet) 분리**: X좌표 클러스터링(`cluster_sheets.py`)으로 Sheet 1, 2, 3... 자동 구분

---

## 3. 상부 조립도 vs 하부 단품도 교차 검도 및 5단계 검증

### 3.1 상부 조립도 vs 하부 단품도 1:1 교차 검도 6대 원칙
1. **타이틀 블록 및 프로젝트명 일관성 검증**: 파일명·상부 도면(`PART NO.`, `PROJECT`, `CUSTOMER`)과 하부 단품도 헤더(`NO. 1`, `NO. 2`...) 대조 (타 프로젝트 템플릿 복사 잔존 문구 적발).
2. **도면 세트(Sheet) 누락 및 세트 수량 점검**: 상부 모든 조립도 대비 하부 단품도 시트 누락, 대칭형(`LH/RH`) 작성 여부, 그리고 단품도 내부 품목 수량이 **1세트 기준인지 총수량 기준인지**(`×4EA`, `×2EA`) 명확히 검증.
3. **형강 마구리(웹/플랜지 공제) 연산 검증**: H-Beam 및 각관 절단 길이에서 접합부 웹/플랜지 두께 공제 검증 (예: `2300 - 200 - 8 = 2092`, `1950 - 8 = 1942`, `700 - 4.5*2 = 691`).
4. **단품 타이틀 텍스트 vs 실제 CAD 형상 불일치 적발**: 복사-붙여넣기 오류로 타이틀만 이전 품목으로 남은 경우, 실제 Polyline 외형·홀 개수·상부 도면 두께/전체 홀 수량(`8-Ø27 THRU` ÷ 2홀 = `4EA`)으로 역산 적발.
5. **가공기호(`6.3`, `25` 등) 기반 가공 여유 검증**: `Quote Ekosystem` 실측치 및 `치수(SK)` 완성 치수 대조로 두께/폭/길이 여유 적정성 확인.
6. **DRC / DFM / DFA / DXF 사전 검증**: 중복선(`OVERKILL`), 열린 윤곽선, 치수 단위(`mm`, `1:1`), 탭 깊이(`DP`) 간섭, 모따기(`C5/C30/C50`) 용접 여유 확인 (`references/` 참조).

### 3.2 5단계 누락 단품 및 수량 자동 검증 워크플로우

#### [1단계] 도번(Sheet) 단위 누락 검사
상단 조립도 영역에 존재하는 모든 도번(`DWG NO.`)이 하단 단품도 영역에도 빠짐없이 생성되었는지 확인합니다 (`find_missing_parts.py`).
- **판정**: 조립도 도번 ≠ 단품도 도번 → ❌ **전체 Sheet 누락**

#### [2단계] 단품 라벨 vs 실제 형상 존재 여부 검사
단품 목록 텍스트(예: `1. H200x200...`) 하단 구역에 실제 `LINE`, `CIRCLE`, `ARC`, `LWPOLYLINE` 형상이 작도되어 있는지 확인합니다 (`check_missing_geometries.py`).
- **판정**: 라벨만 있고 형상 객체 0개 → ❌ **단품 형상 누락**

#### [3단계] 조립도 가공 주석 역추적 대조 (Post-Machining Block Detection)
조립도 내 탭/관통홀/키홈 주석에 해당하는 가공 블록 단품이 단품 BOM에서 빠져 있지 않은지 대조합니다 (`verify_specific_parts.py`, `audit_assembly_vs_parts.py`).
- **검색 키워드 패턴** (정규표현식):
  ```
  DP\s*\d+          → 탭(TAP) 깊이 → 가공 블록 필요
  M\d+x\d+          → 미터 나사 → 가공 블록 필요
  Ø\d+\s*THRU       → 관통홀 → 가공 블록 필요
  KEY\s*WAY          → 키홈 → 가공 블록 필요
  양면가공|FACE       → 평면 가공 → 가공 블록 필요
  CHAIN\s*COVER      → 체인 커버 → 가공 블록 필요
  ```
- **판정**: 가공 주석 有, 대응 단품 無 → ❌ **후가공 블록 단품 누락**

#### [4단계] 스티프너/보강리브 수량 전수 카운팅
H-Beam 웹(Web) 내부 등에 용접되는 스티프너(`12tx95x175` 등)는 평면도·정면도의 좌표를 직접 집계합니다 (`count_95x175.py`, `count_stiffeners.py`).
- **계산 공식**: `실제 수량 = (설치 개소 수) × (빔 수량) × (단면/양면 여부)`
- **판정**: BOM 기재 수량 ≠ 집계 수량 → ❌ **스티프너 수량 오기** (예: H-Beam 2개 × 4개소 × 단면 = `8EA`, BOM `6EA` 오기 적발)

#### [5단계] 일반 기하·치수 품질 검도
`inspect_drawing.py`를 활용하여 다음 항목을 추가 점검합니다:
- **치수 위조(Override) 검출**: 형상 길이와 다른 임의 텍스트 수정 치수 적발
- **레이저/CNC 가공 결함 방지**: 중복선(Overlap) 및 `0.1mm` 미만 미소 선분 검출 → `OVERKILL` 권고
- **홀 직경 분포 분석**: 비표준 홀 직경 발견 시 경고

---

## 4. 스크립트 참조 및 오픈소스 도구 실행 가이드

### 4.1 스크립트 참조 테이블 (Script Reference)

| 스크립트 | 용도 | 주요 입력 | 주요 출력 |
|---|---|---|---|
| `scripts/dump_full_drawing.lsp` | AutoCAD COM+LISP 고속 엔티티 덤프 | 활성 DWG | `lisp_dump.txt` |
| `dwg_pipeline.py` | DWG→DXF 무인 변환 | `.dwg` 파일 경로 | `.dxf` 파일 |
| `inspect_drawing.py` | 치수 override, 중복선, 미소선분 검출 | `.dxf` 파일 경로 | 콘솔 리포트 |
| `cluster_sheets.py` | 도곽 기반 Sheet 분리 | `.dxf` 파일 경로 | Sheet 목록(X범위) |
| `find_missing_parts.py` | 조립도↔단품도 도번 대조 | `.dxf` 파일 경로 | 누락 도번 리스트 |
| `check_missing_geometries.py` | 단품 라벨 vs 실제 형상 존재 확인 | `.dxf` 파일 경로 | 형상 누락 항목 |
| `audit_assembly_vs_parts.py` | 조립도 BOM → 단품도 교차 검증 | `.dxf` 파일 경로 | 누락/불일치 리스트 |
| `verify_specific_parts.py` | 특정 가공 블록 단품 존재 확인 | `.dxf`, 치수 조건 | 존재 여부 판정 |
| `compare_bom.py` | BOM 항목 간 수량/치수 비교 | `.dxf` 파일 경로 | 불일치 테이블 |
| `count_95x175.py` | 12tx95x175 스티프너 좌표 카운팅 | `.dxf` 파일 경로 | X좌표별 수량 |
| `count_stiffeners.py` | 범용 스티프너 수량 집계 | `.dxf` 파일 경로 | 총 수량 |
| `analyze_regions.py` | 도면 영역(조립/단품) 자동 구분 | `.dxf` 파일 경로 | 영역 경계 좌표 |
| `generate_shop_drawing.py` | 단품 가공도 자동 생성 | 형강 규격, 치수 | `.dxf` + `.lsp` |
| `detect_weld_symbols.py` | YOLO 기반 용접 기호 15종 자동 인식 | 도면 이미지(`.png`) | 바운딩박스/신뢰도 |

### 4.2 실행 예시: 전체 DXF 파이프라인
```powershell
uv run --with ezdxf python dwg_pipeline.py "신규도면.dwg"
uv run --with ezdxf python cluster_sheets.py "신규도면.dxf"
uv run --with ezdxf python find_missing_parts.py "신규도면.dxf"
uv run --with ezdxf python check_missing_geometries.py "신규도면.dxf"
uv run --with ezdxf python audit_assembly_vs_parts.py "신규도면.dxf"
uv run --with ezdxf python count_stiffeners.py "신규도면.dxf"
uv run --with ezdxf python inspect_drawing.py "신규도면.dxf"
```

### 4.3 설치 완료된 주요 오픈소스 도구 (`tools/` & `.venv`)

| 프로젝트 | 설치 경로 | 핵심 기능 | 실행 환경 및 방법 |
|---|---|---|---|
| `ezdxf` (v1.4.5) | `.venv` 전역 | DXF 2D/3D 파싱, BOM/치수/도곽 추출 | `.\.venv\Scripts\python <script.py>` |
| `weldCalloutIdentifier` | `tools/weldCalloutIdentifier` | YOLO 기반 용접 기호 15종 자동 인식 | `.\.venv\Scripts\python detect_weld_symbols.py <도면이미지.png>` |
| `sw-drawing-qc` | `tools/sw-drawing-qc` | DXF/PDF 도면 품질 검사, ISO 2553/2768 | `skills/sw-drawing-qc.md`, `skills/sw-drawing-qc-pro.md` 규칙 적용 |
| `ConstructDrawingAI` | `tools/ConstructDrawingAI` | 2D 기술 도면 구조화 및 수량 산출(Takeoff) | `.\.venv\Scripts\python tools/ConstructDrawingAI/backend/app.py` |
| `FreeCAD_SheetMetal` | `tools/FreeCAD_SheetMetal` | 판금 굽힘 전개(Unfold), K-factor 계산 | `.\.venv\Scripts\python tools/FreeCAD_SheetMetal/tools/calc-unfold.py` |

---

## 5. 용접 기호, 조인트 검증 및 검도 체크리스트

### 5.1 필수 용접 기호 체크 항목 & 주요 조인트 패턴
| 항목 | 확인 내용 |
|---|---|
| 기호 위치 | 화살표 쪽(Arrow Side) / 반대쪽(Other Side) 구분 정확성 |
| 용접 유형 | 필릿(Fillet), 그루브(Groove), 플러그(Plug) 등 적합성 |
| 용접 치수 | 각장(Leg Size), 루트 간격(Root Opening), 용입 깊이 |
| 보조 기호 | 전둘레(All-Around ○), 현장(Field ▶), 마무리(Contour) |
| 꼬리 주기 | 용접 프로세스(FCAW, SAW 등), 비파괴검사(NDT) 요구사항 |

```
├─ H-Beam 웹 ↔ 플랜지    : 양쪽 필릿 연속 용접
├─ 스티프너 ↔ 웹          : 양쪽 필릿, 필요 시 완전 용입
├─ 가공 블록 ↔ 본체       : 완전 용입 그루브 (가공 정밀도 확보)
├─ 베이스 플레이트 ↔ 컬럼 : 완전 용입 또는 부분 용입 그루브
├─ 보강 거셋 ↔ 프레임     : 필릿 또는 부분 용입
└─ 앵커 볼트 ↔ 플레이트   : 전둘레 필릿
```

### 5.2 검도 체크리스트 (Quick Manual Checklist)
- [ ] 조립도 모든 Sheet에 대응하는 단품도가 존재하는가? (대칭형 `LH/RH` 포함)
- [ ] BOM 항목 수 = 실제 작도된 단품도 수인가? (품번 누락/공백 없음 확인)
- [ ] 단품 타이틀 텍스트(`12tx...`)가 실제 Polyline 외형/두께/홀 개수와 일치하는가?
- [ ] 탭/보링/키홈 등 가공 주석마다 대응 가공 블록 단품이 있는가?
- [ ] 가공기호(`6.3`, `25`) 면에 Blank Allowance(두께/폭/길이 여유)가 반영되어 있는가?
- [ ] 형강(H-Beam/각관/파이프) 절단 길이에 마구리/웹/플랜지 공제가 정확히 반영되었는가?
- [ ] 스티프너/보강리브 수량이 조립도 배치와 일치하는가?
- [ ] 치수 Override(임의 수정 치수), 중복선, 0.1mm 미만 미소 선분이 없는가?
- [ ] 용접 기호 및 선가공(`PRE-MACHINING`) 주기가 누락 없이 표기되어 있는가?

---

## 6. 알려진 DXF / AutoLISP 파싱 주의사항

| 문제 | 원인 | 대응 |
|---|---|---|
| `POLYLINE` vs `LWPOLYLINE` | 구버전 DWG의 3D 폴리라인은 `get_points()` 없음 | `LWPOLYLINE`만 쿼리하거나 `vertices`/`Coordinates` 속성 사용 |
| MText 서식 코드 | `{\fArial;H200x200}` 같은 서식이 텍스트에 혼입 | 정규표현식으로 `{\...;}` 사전 제거 |
| CP949 인코딩 | 한글 레이어명/텍스트 깨짐 | `ezdxf.readfile(path, encoding='cp949')`, LISP는 `encoding='cp949'` 저장 |
| 좌표계 혼용 | UCS/WCS 혼용 시 좌표 오차 | `(trans pt 1 0)`으로 WCS 통일 (LISP), ezdxf는 OCS→WCS 변환 |
| 치수 텍스트 위조 | `dxf.text` / DXF group `1`에 override 문자열 존재 | 측정값(`42`)과 `text` 필드 비교하여 불일치 적발 |

---

## 7. 누적 검도 지식 베이스 (Inspection Knowledge Log)

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

---

## 8. 버전 이력

| 버전 | 일시 | 내용 |
|---|---|---|
| v1.0 | 2025-11-25 | 초기 스킬 작성 (3단계 검증, 후가공 원칙) |
| v1.1 | 2025-11-25 | 5단계 검증 확장, Blank Allowance 테이블 추가 |
| v2.0 | 2026-11-25 | 스크립트 참조 테이블, 체크리스트, 용접 기호 규칙, 오픈소스 참조, DXF 주의사항 대폭 추가 |
| v2.1 | 2026-11-25 | 오픈소스 도구 5종 최신 설치 및 `.venv` 환경 구축, `detect_weld_symbols.py` 래퍼 연동 |
| v3.0 | 2026-11-26 | `cad-fabrication-inspection` + `metal-fabrication-qa` 통합: AutoCAD COM+LISP 고속 덤프, 6대 교차 검도, `AI_MOD_BOX`/`AI_CP` 표준, DRC/DFM/DFA/DXF 레퍼런스 및 누적 검도 케이스 로그(Case 01~02) 병합 |
