---
name: metal-fabrication-qa
description: >-
  제관, 용접 및 기계 후가공(5면가공기/보링 등) 도면 전수 검도 및 단품가공도 누락 검증 스킬.
  조립도와 단품도 간의 누락 단품, 스티프너/보강리브 수량 오류, 후가공 소재 여유 치수(Blank Allowance) 반영 여부를 자동 점검할 때 사용합니다.
---

# 제관·용접·후가공 도면 검도 (Metal Fabrication & Machining QA)

제관·용접 구조물 및 기계 후가공 도면을 분석·검도할 때 반드시 아래의 실무 원칙과 검증 절차를 수행합니다.

---

## 1. 제관 및 선/후가공 대원칙 (Engineering Rules)

### 1.1 후가공 원칙 (Post-Machining Default)
- 모든 제관·용접 구조물의 정밀 가공면, 탭(TAP), 리머/보링 홀은 **용접 완료 후 후가공(5면가공기, 보링기 등)을 원칙**으로 합니다.
- 후가공 대상 가공 유형:
  | 가공 유형 | 대표 주석 키워드 | 설명 |
  |---|---|---|
  | 탭(TAP) 가공 | `M16x2 DP 46`, `M24x3 DP 60` | 볼트 체결용 암나사 |
  | 관통홀 | `Ø27 THRU`, `Ø22 관통` | 볼트/핀 관통 구멍 |
  | 보링 가공 | `Ø98 양면가공`, `Ø120H7` | 베어링/부시 삽입면 |
  | 키홈 가공 | `KEY WAY 28x7`, `KEY 25x14` | 축-허브 결합용 |
  | 평면 가공 | `양면가공`, `FACE MILLING` | 접합면 평탄도 확보 |
  | 체인 커버 | `CHAIN COVER` | 커버 볼트 패턴 가공 |

### 1.2 후가공 소재 여유 치수 (Blank Allowance)
- 후가공이 들어가는 단품은 단품도 및 BOM 발주 치수에 **가공 여유를 포함한 원자재 소재 치수**로 등록해야 합니다.
- **표준 가공 여유 테이블**:

  | 완성 치수 (t) | 가공 방향 | Blank 여유 | 발주 치수 (t) | 비고 |
  |---|---|---|---|---|
  | ≤ 30mm | 한쪽 면 | +3~4mm | 완성t + 4mm | 소형 블록 |
  | 31~60mm | 한쪽 면 | +4~5mm | 완성t + 4mm | **기본 적용** |
  | 31~60mm | 양면 | +8~10mm | 완성t + 8mm | 양면 가공 |
  | 61~100mm | 한쪽 면 | +5~6mm | 완성t + 5mm | 중형 블록 |
  | > 100mm | 한쪽 면 | +6~8mm | 완성t + 6mm | 대형·특수 |

  > **실무 예시**: 조립도 완성 두께 `46t` + `4-M16x2 DP 46` 탭 가공 블록(`46x250x280`)인 경우,
  > 단품도에는 **`50Tx250x280-1EA`**(가공 후 `46t`)로 작성되어야 합니다.

### 1.3 선가공 예외 원칙 (Pre-Machining Only Where Inaccessible)
- 용접 조립 후 가공 공구(스핀들/홀더)가 진입할 수 없거나 구조물과 간섭이 발생하는 협소한 내부 부위만 **선가공(Pre-Machining) 후 부착** 대상으로 분류합니다.
- 선가공 판단 기준:
  - 공구 진입 경로(Spindle Clearance)가 확보되지 않는 내부 포켓
  - 용접 열변형으로 치수 보정이 불가능한 고정밀 조립면 (IT7 이상)
  - 용접 후 열처리(SR 처리) 뒤에도 가공이 불가능한 위치

---

## 2. 도면 변환 및 검도 실행 절차 (Workflow)

### Step 1: 무인 DWG → DXF 고속 변환
AutoCAD GUI를 띄우지 않고 `dwg_pipeline.py`를 통해 `accoreconsole.exe`로 무손실 DXF를 추출합니다.
```powershell
uv run --with ezdxf python dwg_pipeline.py "<대상도면.dwg>"
```

### Step 2: 조립도/단품도 영역 자동 분리
DXF 파일에서 Y좌표 기반으로 조립도 영역(상단)과 단품도 영역(하단)을 자동 분리합니다.
- **조립도 영역**: Y > -75,000 (일반적)
- **단품도 BOM/형상 영역**: Y < -104,000 (일반적)
- **도번(Sheet) 분리**: X좌표 클러스터링으로 Sheet 1, 2, 3... 자동 구분
  - `cluster_sheets.py` — 도곽 LWPOLYLINE의 X범위로 Sheet 분리

### Step 3: 5단계 누락 단품 및 수량 교차 검증

#### [1단계] 도번(Sheet) 단위 누락 검사
상단 조립도 영역에 존재하는 모든 도번(`DWG NO.`)이 하단 단품도 영역에도 빠짐없이 생성되었는지 확인합니다.
- 사용 스크립트: `find_missing_parts.py`
- **판정**: 조립도 도번 ≠ 단품도 도번 → ❌ **전체 Sheet 누락**

#### [2단계] 단품 라벨 vs 실제 형상 존재 여부 검사
단품 목록 텍스트(예: `1. H200x200...`) 하단 구역에 실제 `LINE`, `CIRCLE`, `ARC`, `LWPOLYLINE` 형상이 작도되어 있는지 확인합니다.
- 사용 스크립트: `check_missing_geometries.py`
- **판정**: 라벨만 있고 형상 객체 0개 → ❌ **단품 형상 누락**

#### [3단계] 조립도 가공 주석 역추적 대조 (Post-Machining Block Detection)
조립도 내 탭/관통홀/키홈 주석에 해당하는 가공 블록 단품이 단품 BOM에서 아예 빠져 있지 않은지 대조합니다.
- **검색 키워드 패턴** (정규표현식):
  ```
  DP\s*\d+          → 탭(TAP) 깊이 → 가공 블록 필요
  M\d+x\d+          → 미터 나사 → 가공 블록 필요
  Ø\d+\s*THRU       → 관통홀 → 가공 블록 필요
  KEY\s*WAY          → 키홈 → 가공 블록 필요
  양면가공|FACE       → 평면 가공 → 가공 블록 필요
  CHAIN\s*COVER      → 체인 커버 → 가공 블록 필요
  ```
- **대조 로직**: 가공 주석이 발견되면 → 주변에 해당 블록 치수 텍스트 추출 → 단품 BOM에서 Blank Allowance 적용된 치수로 존재 확인
- 사용 스크립트: `verify_specific_parts.py`, `audit_assembly_vs_parts.py`
- **판정**: 가공 주석 有, 대응 단품 無 → ❌ **후가공 블록 단품 누락**

#### [4단계] 스티프너/보강리브 수량 전수 카운팅
H-Beam 웹(Web) 내부 등에 용접되는 스티프너(`12tx95x175` 등)는 평면도·정면도의 좌표를 직접 집계합니다.
- **계산 공식**: `실제 수량 = (설치 개소 수) × (빔 수량) × (단면/양면 여부)`
- 사용 스크립트: `count_95x175.py`, `count_stiffeners.py`
- **판정**: BOM 기재 수량 ≠ 집계 수량 → ❌ **스티프너 수량 오기**
  > **실무 예시**: H-Beam 2개 × 4개소 × 단면 = **8EA** (BOM에 `6EA`로 오기된 사례 적발)

#### [5단계] 일반 기하·치수 품질 검도
`inspect_drawing.py`를 활용하여 다음 항목을 추가 점검합니다:
- **치수 위조(Override) 검출**: 형상 길이와 다른 임의 텍스트 수정 치수 적발
- **레이저/CNC 가공 결함 방지**: 중복선(Overlap) 및 `0.1mm` 미만 미소 선분 검출 → `OVERKILL` 권고
- **홀 직경 분포 분석**: 비표준 홀 직경 발견 시 경고

---

## 3. 스크립트 참조 테이블 (Script Reference)

| 스크립트 | 용도 | 주요 입력 | 주요 출력 |
|---|---|---|---|
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

---

## 4. 실행 예시: 전체 파이프라인 (Full Pipeline Example)

새 DWG 파일을 받았을 때의 전체 검도 절차:

```powershell
# 1. DWG → DXF 변환
uv run --with ezdxf python dwg_pipeline.py "신규도면.dwg"

# 2. Sheet 클러스터링 (도곽 기반)
uv run --with ezdxf python cluster_sheets.py "신규도면.dxf"

# 3. 조립도↔단품도 누락 대조
uv run --with ezdxf python find_missing_parts.py "신규도면.dxf"

# 4. 단품 형상 존재 여부 확인
uv run --with ezdxf python check_missing_geometries.py "신규도면.dxf"

# 5. 조립도 가공 주석 역추적
uv run --with ezdxf python audit_assembly_vs_parts.py "신규도면.dxf"

# 6. 스티프너 수량 전수 카운팅
uv run --with ezdxf python count_stiffeners.py "신규도면.dxf"

# 7. 치수·기하 품질 검사
uv run --with ezdxf python inspect_drawing.py "신규도면.dxf"
```

---

## 5. 검도 체크리스트 (Quick Manual Checklist)

도면 수신 후 AI 자동 검도와 병행하여 육안 확인할 항목:

- [ ] 조립도 모든 Sheet에 대응하는 단품도가 존재하는가?
- [ ] BOM 항목 수 = 실제 작도된 단품도 수인가?
- [ ] 탭/보링/키홈 등 가공 주석마다 대응 가공 블록 단품이 있는가?
- [ ] 가공 블록 치수에 Blank Allowance(+4~5mm)가 반영되어 있는가?
- [ ] 스티프너/보강리브 수량이 조립도 배치와 일치하는가?
- [ ] 치수 Override(임의 수정 치수)가 없는가?
- [ ] 중복선이나 0.1mm 미만 미소 선분이 없는가?
- [ ] 용접 기호가 필요한 모든 조인트에 표기되어 있는가?
- [ ] 선가공 부위에 `선가공` 또는 `PRE-MACHINING` 주기가 있는가?
- [ ] 표면 거칠기(Ra) 기호가 가공면에 명기되어 있는가?

---

## 6. 용접 기호 및 조인트 검증 규칙 (Weld Symbol Rules)

### 6.1 필수 용접 기호 체크 항목
| 항목 | 확인 내용 |
|---|---|
| 기호 위치 | 화살표 쪽(Arrow Side) / 반대쪽(Other Side) 구분 정확성 |
| 용접 유형 | 필릿(Fillet), 그루브(Groove), 플러그(Plug) 등 적합성 |
| 용접 치수 | 각장(Leg Size), 루트 간격(Root Opening), 용입 깊이 |
| 보조 기호 | 전둘레(All-Around ○), 현장(Field ▶), 마무리(Contour) |
| 꼬리 주기 | 용접 프로세스(FCAW, SAW 등), 비파괴검사(NDT) 요구사항 |

### 6.2 제관 구조물 주요 용접 조인트 패턴
```
├─ H-Beam 웹 ↔ 플랜지    : 양쪽 필릿 연속 용접
├─ 스티프너 ↔ 웹          : 양쪽 필릿, 필요 시 완전 용입
├─ 가공 블록 ↔ 본체       : 완전 용입 그루브 (가공 정밀도 확보)
├─ 베이스 플레이트 ↔ 컬럼 : 완전 용입 또는 부분 용입 그루브
├─ 보강 거셋 ↔ 프레임     : 필릿 또는 부분 용입
└─ 앵커 볼트 ↔ 플레이트   : 전둘레 필릿
```

---

## 7. 설치 완료된 주요 오픈소스 도구 및 실행 가이드

프로젝트 `tools/` 디렉터리에 설치 완료된 최신 오픈소스 도구와 실행 방법:

| 프로젝트 | 설치 경로 | 핵심 기능 | 실행 환경 및 방법 |
|---|---|---|---|
| `ezdxf` (v1.4.5) | `.venv` 전역 | DXF 2D/3D 파싱, BOM/치수/도곽 추출 | `.\.venv\Scripts\python <script.py>` |
| `weldCalloutIdentifier` | `tools/weldCalloutIdentifier` | YOLO 기반 용접 기호 15종 자동 인식 | `.\.venv\Scripts\python detect_weld_symbols.py <도면이미지.png>` |
| `sw-drawing-qc` | `tools/sw-drawing-qc` | DXF/PDF 도면 품질 검사, ISO 2553/2768 | `skills/sw-drawing-qc.md`, `skills/sw-drawing-qc-pro.md` 규칙 적용 |
| `ConstructDrawingAI` | `tools/ConstructDrawingAI` | 2D 기술 도면 구조화 및 수량 산출(Takeoff) | `.\.venv\Scripts\python tools/ConstructDrawingAI/backend/app.py` |
| `FreeCAD_SheetMetal` | `tools/FreeCAD_SheetMetal` | 판금 굽힘 전개(Unfold), K-factor 계산 | `.\.venv\Scripts\python tools/FreeCAD_SheetMetal/tools/calc-unfold.py` |

### 7.1 용접 기호 AI 자동 검출기 실행 예시
AWS/ISO 용접 기호 15종(Fillet, Groove, Tail, All-Around 등) 자동 인식:
```powershell
.\.venv\Scripts\python detect_weld_symbols.py "tools/weldCalloutIdentifier/assets/weldExamples/example1.png"
```
*출력 예시:*
```text
=== DETECTED WELD SYMBOLS: 3 items ===
 - calloutTail: conf=0.911 bbox=[438, 22, 471, 86]
 - filletWeld: conf=0.888 bbox=[318, 48, 386, 117]
 - calloutTip: conf=0.608 bbox=[50, 221, 69, 261]
```

### 7.2 판금 절곡(Bend) & 전개 치수 계산기 실행 예시
내측 반경(r), 판두께(T), K-factor, 절곡 각도 기반 전개장(BA) 계산:
```powershell
.\.venv\Scripts\python tools/FreeCAD_SheetMetal/tools/calc-unfold.py
```

---

## 8. 알려진 DXF 파싱 주의사항

| 문제 | 원인 | 대응 |
|---|---|---|
| `POLYLINE` vs `LWPOLYLINE` | 구버전 DWG의 3D 폴리라인은 `get_points()` 없음 | `LWPOLYLINE`만 쿼리하거나 `vertices` 속성 사용 |
| MText 서식 코드 | `{\fArial;H200x200}` 같은 서식이 텍스트에 혼입 | 정규표현식으로 `{\...;}` 사전 제거 |
| CP949 인코딩 | 한글 레이어명/텍스트 깨짐 | `ezdxf.readfile(path, encoding='cp949')` 시도 |
| 좌표계 혼용 | UCS/WCS 혼용 시 좌표 오차 | `(trans pt 1 0)`으로 WCS 통일 (LISP), ezdxf는 OCS→WCS 변환 |
| 치수 텍스트 위조 | `dxf.text` 필드에 override 문자열 존재 | 측정값과 `text` 필드 비교하여 불일치 적발 |

---

## 9. 버전 이력

| 버전 | 일시 | 내용 |
|---|---|---|
| v1.0 | 2025-11-25 | 초기 스킬 작성 (3단계 검증, 후가공 원칙) |
| v1.1 | 2025-11-25 | 5단계 검증 확장, Blank Allowance 테이블 추가 |
| v2.0 | 2026-11-25 | 스크립트 참조 테이블, 체크리스트, 용접 기호 규칙, 오픈소스 참조, DXF 주의사항 대폭 추가 |
| v2.1 | 2026-11-25 | 오픈소스 도구 5종 최신 설치 및 .venv 환경 구축, detect_weld_symbols.py 래퍼 연동 |
