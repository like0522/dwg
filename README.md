# DWG Automation & DXF Headless Pipeline

AutoCAD DWG 도면의 무인(Headless) 고속 DXF 변환 및 정밀 파싱/분석 자동화 리포지토리입니다.

## 기능 특징
- **AutoCAD accoreconsole 연동**: GUI 없이 1~2초 만에 DWG를 DXF로 완전 무손실 변환
- **ezdxf 기반 고속 분석**: 도면 내 도면층(Layer), 블록 참조(INSERT), 텍스트/치수, 엔티티별 수량 자동 집계
- **AutoLISP & COM Bridge 호환**: 필요 시 실시간 CAD 제어 및 LISP 자동 생성 지원

## 실행 방법
```powershell
# DWG 변환 및 분석 원샷 실행 (.venv 환경)
.\.venv\Scripts\python dwg_pipeline.py "도면명.dwg"

# 용접 기호 AI 자동 검출 (YOLO)
.\.venv\Scripts\python detect_weld_symbols.py "도면이미지.png"
```

## 통합 검도 스킬
- [.agents/skills/metal-fabrication-qa/SKILL.md](.agents/skills/metal-fabrication-qa/SKILL.md) (v3.1)
