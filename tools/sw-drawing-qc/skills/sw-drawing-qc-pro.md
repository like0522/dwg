---
name: sw-drawing-qc-pro
description: SolidWorks 工程图 QC 检查 Pro v2.0——ezdxf 结构化解析 DXF + 国标库(GB/T 1804/1184/131/4458) + 特征识别(轴承孔/键槽/螺纹/倒角/圆角/孔组) + PDF 支持 + 7 大行业规则预设(汽车/模具/钣金/焊接/液压/齿轮/GB基线) + JSON/Excel 双格式报告。面向机械设计师和制造企业。
---

# 工程图 QC 检查 Pro v2.0

## 架构概览

```
sw_qc_parser.py          ← 主入口 (DXF/PDF 统一入口)
    ├── sw_qc_gb.py      ← 国标库 (GB/T 1804/1184/131/4458/4459)
    ├── sw_qc_features.py ← 特征识别 (轴承孔/键槽/螺纹/倒角/圆角/孔组/退刀槽/中心孔)
    ├── sw_qc_pdf.py     ← PDF 支持 (pymupdf 文本+矢量提取)
    ├── sw_qc_rules.py   ← 规则引擎 (7 大行业预设 + YAML 自定义)
    └── sw_qc_parser.py  ← 核心解析 + Excel 生成
```

---

## 快速开始

### 安装依赖

```bash
pip install ezdxf openpyxl pymupdf pyyaml
```

### 基础用法

```bash
# DXF 检查（标准模式）
python sw_qc_parser.py 图纸.dxf

# DXF + 特征识别 + 国标规则
python sw_qc_parser.py 图纸.dxf --features --rules gb_baseline

# 完整输出（JSON + Excel）
python sw_qc_parser.py 图纸.dxf --features --rules automotive --json --excel

# PDF 检查
python sw_qc_parser.py 图纸.pdf --pdf --json

# 批量检查
for f in /path/to/drawings/*.DXF; do
    python sw_qc_parser.py "$f" --features --rules gb_baseline --json --excel
done
```

---

## 模块详情

### 一、国标库 (`sw_qc_gb.py`)

| 标准 | 涵盖 |
|------|------|
| **GB/T 1804** | 一般公差：线性尺寸(f/m/c/v)、倒角/倒圆、角度尺寸 完整数据表 |
| **GB/T 1184** | 形位公差未注值：直线度/平面度/垂直度/对称度/圆跳动/同轴度 (H/K/L) |
| **GB/T 131** | 粗糙度：Ra 系列值、公差-粗糙度匹配表、特征推荐 |
| **GB/T 4458** | 图样画法：幅面(A0-A4)、比例、线宽、标题栏字段 |
| **GB/T 4459** | 结构要素：螺纹标注验证、退刀槽尺寸、中心孔类型 |
| **推荐引擎** | 10 种特征类型 → 推荐的公差+形位公差+粗糙度 |

### 二、特征识别 (`sw_qc_features.py`)

自动检测的 8 种机械特征：

| 特征 | 检测方法 | 置信度 | GB 推荐联动 |
|------|----------|--------|-------------|
| 轴承安装孔 | 同心多圆 + 中心标记 + 半径差 | 90-100% | H7 + 圆柱度 + Ra 0.4-0.8 |
| 轴承安装轴肩 | 同心圆 + 轴肩线 | 85-95% | h6 + 圆跳动 + Ra 0.4-0.8 |
| 键槽 | 平行线对 + 端弧 + 长宽比 | 40-90% | N9 + 对称度 + Ra 1.6-3.2 |
| 螺纹孔 | 圆 + 附近 M/G/Rc 开头的标注文字 | 85% | 6H + 垂直度 |
| 倒角 | 短线 + 45°夹角 | 65-75% | C 值标注 |
| 圆角 | 小半径弧 + 连接线 | 65% | R 值标注 |
| 孔组(阵列) | 3+ 等径圆直线/圆周排列 | 70-85% | 位置度 |
| 退刀槽 | 小弧 + 轴侧短线 | 50% | GB/T 6403.5 |

### 三、PDF 支持 (`sw_qc_pdf.py`)

- 使用 `pymupdf` 提取文本块 + 词级别文字
- 尺寸/公差/粗糙度文本自动识别
- 矢量线条统计
- 标题栏右下角自动定位
- 适用场景：甲方只给 PDF、旧图纸扫描后 OCR

### 四、规则引擎 (`sw_qc_rules.py`)

7 大内置行业预设：

| 预设 | 适用领域 | 特色规则 |
|------|----------|----------|
| `gb_baseline` | 通用（基线） | 材料必填、尺寸必标、GB/T 1804/1184 引用 |
| `automotive` | 汽车零部件 | IATF 16949、PPAP、清洁度 |
| `mold` | 模具 | 拔模斜度、硬度、成型面 Ra |
| `sheet_metal` | 钣金 | 展开图、折弯半径、板厚 |
| `welding` | 焊接结构 | 焊接符号 GB/T 324、探伤、去应力 |
| `hydraulic` | 液压件 | 密封面 Ra 0.2-0.4、清洁度 ISO 4406、试压 |
| `gear` | 齿轮 | 参数表(模数/齿数/压力角)、精度 GB/T 10095 |

支持 5 种规则匹配模式：`always`、`field_check`、`feature_check`、`count_threshold`、`text_contains`。

自定义规则通过 YAML 文件添加，格式见 `rules/` 目录。

---

## 输出格式

### Markdown 报告（Claude 生成）

完整的结构化 QC 报告，包含：
- 基本信息 + 问题汇总（🔴🟡🟢）
- 逐项检查结果（尺寸/公差/粗糙度/文本/视图）
- 特征识别详情 + GB 推荐标注
- 规则预设检查结果
- 50 分制完整性评分
- 优先修改建议 Top 3

### JSON 输出 (`--json`)

```json
{
  "engine_version": "Pro v2.0",
  "info": { "acad_version": "AC1015", ... },
  "dim_data": { "count": 0, "dimensions": [...], ... },
  "features": [{ "type": "轴承安装孔", "confidence": 1.0, ... }],
  "checks": [...],
  "rule_preset": "gb_baseline"
}
```

### Excel 报告 (`--excel`)

多 Sheet 工作簿：QC 汇总 / 尺寸统计 / 标题栏，带颜色编码。

---

## 与免费版对比

| | 免费版 (`sw-drawing-qc`) | Pro v2.0 (`sw-drawing-qc-pro`) |
|---|---|---|
| DXF 解析 | 文本扫描 | ezdxf 结构化实体提取 |
| 国标库 | 口头引用 | 完整数据表 + 自动查值 |
| 特征识别 | ❌ | 8 种机械特征自动识别 |
| PDF 支持 | ❌ | pymupdf 文本+矢量 |
| 规则引擎 | ❌ | 7 行业预设 + YAML 自定义 |
| 报告格式 | Markdown | Markdown + JSON + Excel |
| 批量处理 | ❌ | 循环脚本 |

---

## 完整使用示例

```bash
# Step 1: 运行解析器
python sw_qc_parser.py 杠杆1.DXF --features --rules gb_baseline --json --excel

# Step 2: 读取 JSON 给 Claude（本 Skill）
# Claude 会按国标逐项审查，生成完整 Markdown 报告

# Step 3: 查看 Excel 报告
# 杠杆1.qc_report.xlsx → 可打印签审
```

---

## 目录结构

```
~/.claude/skills/
├── sw-drawing-qc.md       # 免费版 SKILL
├── sw-drawing-qc-pro.md   # Pro 版 SKILL (本文件)
├── sw_qc_parser.py        # 主解析器 (集成入口)
├── sw_qc_gb.py            # 国标库
├── sw_qc_features.py      # 特征识别
├── sw_qc_pdf.py           # PDF 支持
├── sw_qc_rules.py         # 规则引擎
└── rules/                 # 自定义规则目录
    ├── gb_baseline.yaml
    ├── automotive.yaml
    └── ...
```
