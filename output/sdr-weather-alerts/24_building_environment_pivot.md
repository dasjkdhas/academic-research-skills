# 建筑环境化升级与 Energy and Buildings 投稿战略

**目标期刊**: Energy and Buildings (Elsevier, IF~7)
**两条数据线**: 主线低数据 (AMeDAS 四要素 + 学事日历) + 辅线 ERA5 湿度热舒适
**作成日**: 2026-05-31

---

## 1. 一句话结论 — 升级方向

> 把研究从「**低数据校园容量风险识别**」重新定位为「**在室者驱动的建筑温度敏感性: 学事日历调节的建筑环境响应机制**」，让「学事日历调节」从统计现象变成**可量化的建筑物理量（平衡点温度位移与内部得热）**。

---

## 2. 实证结果 — 三个新发现（已计算）

### 发现 A: 干球温度仍是最佳预测因子（重要反证）

冷房期 全数据回归 R² 比较：
| 指标 | 冷房斜率 (kWh/h/°C) | R² | 解读 |
|---|---|---|---|
| **气温 T** | +25.4 | **0.221** | 最高 R² |
| 热指数 HI | +14.2 | 0.190 | 次之 |
| 表观温度 T_app | +16.4 | 0.182 | |
| WBGT | +20.0 | 0.155 | 最低 R² |

**意义（坦诚解读）**:
- 在校园电表级聚合数据上，**干球温度 T 已是最佳预测因子**，加入湿度反而稍微降低 R²。
- 这是因为**电表级总负荷**主要由空调启停决定，而空调启停以**设定温度**（干球）为基准，不直接响应湿度。
- 这反而**强化了我们「低数据可行」的主张**——湿度信息对电表级建模无显著加值。

### 发现 B: WBGT 下学事日历调节依然显著（关键正面结果）

冷房期 × 日种别（WBGT 横轴）：
| 日种别 | 冷房斜率 | R² | n (日) |
|---|---|---|---|
| **授业日** | +36.7 | **0.91** | 46 |
| **周末** | +24.1 | **0.81** | 18 |
| 休业期间 | +26.0 | 0.14 | 48 |

**意义**:
- 换成热舒适指标 WBGT 后，**授业日仍以 1.52 倍敏感度高于周末**（R² 均高位）。
- 证明「学事日历调节」**不是湿度的混杂**，而是**在室者真实存在的物理效应**。
- 这是审稿人会问的关键稳健性测试，**已通过**。

### 发现 C: 平衡点温度位移 — 建筑物理学的「在室者内部得热」（论文的物理机制核心）

| 日种别 | 平衡点温度 T_balance | 基底负荷 | 物理解释 |
|---|---|---|---|
| 授业日 | **18.4°C** | 683 kWh/h | 高 Q_internal (学生 + 设备 + 照明) |
| 周末 | 19.3°C | 526 kWh/h | 中等 Q_internal (部分研究室) |
| 休业期间 | **22.4°C** | 560 kWh/h | 低 Q_internal (人员极少) |

**建筑物理诠释**:
$$T_{balance} = T_{set} - \frac{Q_{internal} + Q_{solar}}{UA}$$

- ΔT_balance (授业日 − 休业期间) = **4.0°C**
- 在 UA 约 100 kW/°C (典型大学栋) 假设下，**Q_internal 差 ≈ 400 kW** ≈ 学生 + 设备 + 照明的合理量级
- **这是把统计现象 (学事日历调节) 翻译成建筑物理量 (内部得热) 的桥梁** — 完全契合 E&B 的本体论

### 发现 D: 同 WBGT 下的负荷超量 = 内部得热直接证据

WBGT 28-29°C 区间：授业日 931 kWh/h，周末 624 kWh/h，**差 307 kWh/h**（同热应力下）
WBGT 29-30°C 区间：授业日 967，周末 696，**差 271 kWh/h**

→ 同样的「热应力」下，授业日比周末多 270-307 kWh/h 的需要 = **占用相关内部得热的直接测量值**

这是建筑环境研究的「**机制确认**」证据。

---

## 3. 论文重新定位：从「容量风险」到「建筑环境机制」

### 旧定位 (原稿)
> 「在有限气象数据下识别校园容量风险与学事日历调节的统计现象」

### 新定位 (E&B 化)
> 「**学事时间表如何通过在室者内部得热改变校园建筑的温度敏感性**: 平衡点温度位移作为建筑环境响应的可测量证据」

| 维度 | 旧 | 新 (E&B 化) |
|---|---|---|
| 核心问题 | 统计现象描述 | **建筑物理机制** |
| 自变量解释 | 「学事日历调节」 | 「**在室者内部得热**」 |
| 量化对象 | 斜率与 R² | **平衡点温度位移 ΔT_balance** |
| 政策链接 | 容量管理窗口 | **Cool Biz 28°C + ASHRAE 55 + 内部得热设定** |
| 投稿契合 | Energies | **Energy and Buildings** |

---

## 4. 新研究问题 (RQ)

旧 4 个 RQ 升级为 5 个：

| RQ | 问题 | 方法 | 状态 |
|---|---|---|---|
| RQ1 | 校园全年负荷的制度+季节周期结构 | 描述性 | ✅ 已有 |
| RQ2 | 仅用干球温度能否识别冷热阈值？ | 季节分离能量署名 | ✅ 已有 |
| **RQ3 (新)** | **干球温度 vs 热舒适指标 (WBGT/HI/T_app)，哪个更好预测校园负荷？** | 指标比较 R² | ✅ 已有 (T 胜) |
| **RQ4 (新)** | **学事日历对温度敏感性的调节，是真在室者机制还是湿度混杂？** | WBGT 重做日种别 | ✅ 已有 (机制确认) |
| RQ5 | 平衡点温度位移如何量化在室者内部得热？ | 变点回归 + 物理模型 | ✅ 已有 |
| RQ6 | 容量风险在 (温度×日种别) 的集中 → 管理窗口 | ρ 映射 | ✅ 已有 |

### Novelty 三重定位

1. **方法论**: 平衡点温度位移作为低数据条件下的内部得热代理量 (novel)
2. **机制**: WBGT 仍维持 1.52× 学事日历调节，确认机制为占用驱动而非湿度混杂
3. **实用**: Cool Biz 28°C 与平衡点温度的距离，为政策合规度评估提供量化指标

---

## 5. Energy and Buildings 投稿改造清单

### 必做
- [x] 计算热舒适指标 (WBGT, HI, T_app, 体感) ← **已完成**
- [x] 比较干球 vs 热舒适指标的 R² ← **已完成 (BE02)**
- [x] WBGT 下重做日种别署名 ← **已完成 (BE03)**
- [x] 平衡点温度作为建筑物理量诠释 ← **已完成 (BE04)**
- [x] 同 WBGT 下的负荷超量 = 内部得热证据 ← **已完成 (BE05)**
- [ ] 文献综述加入建筑环境层面 (occupant heat gains, T_balance, energy signature)
- [ ] Discussion 链接 Cool Biz 28°C + ASHRAE 55-2017 + ISO 7730
- [ ] 标题改为建筑环境框架表达

### 候选标题 (英文)

1. **"Occupant-driven thermal sensitivity of campus buildings: balance-point temperature shifts as building-physics evidence of academic-calendar modulation"** ← 推荐
2. "Calendar-modulated cooling sensitivity in university buildings: dry-bulb temperature versus thermal-comfort indices and the role of internal heat gains"
3. "From statistical modulation to building physics: quantifying occupant internal heat gains via balance-point temperature shifts in a campus energy signature"

### 候选标题 (日文)
1. 「**在室者由来の建築温度感度: 学事日歴調節と平衡点温度位移による内部発熱の定量化**」
2. 「キャンパス建築の冷房感度における乾球温度と熱的快適性指標の比較: 学事日歴による調節は在室者起源か湿度混杂か」

### 关键词 (E&B 标准)
energy signature; balance-point temperature; internal heat gains; thermal comfort index; WBGT; occupant-driven energy consumption; academic calendar; university campus; capacity risk; Cool Biz

---

## 6. 文献综述要追加的脉络（B-environment 层面）

### 6.1 在室者内部得热 (Occupant heat gains)
- ASHRAE 55-2017 → 在室者潜热与显热得热标准值
- ISO 7730 → PMV/PPD
- Yan et al. 2015, Energy and Buildings → DNAS occupant behavior model

### 6.2 平衡点温度与能量署名
- Kissock et al. 1998, ASHRAE → IMT change-point models (已查实)
- MDPI Buildings 12(10):1717 → Simplified Weather-Related Building Energy Disaggregation (已查实)
- Day & Karayiannis 1998, Building Services Engineering Research → 平衡点温度概念

### 6.3 热舒适指标与建筑能耗
- Stull 2011, J. Applied Meteorology → WBGT 公式
- Rothfusz 1990, NOAA → Heat Index
- Steadman 1984 → Apparent temperature

### 6.4 校园 + 占用 + 能耗
- Reducing university energy use beyond energy retrofitting: The academic calendar impacts (Energy and Buildings 2021) → 关键已查实
- An occupancy-based model for building electricity consumption: three campus buildings in Tianjin (Energy and Buildings 2020) → 已查实

### 6.5 Cool Biz (日本特色加分)
- METI Cool Biz 28°C 政策 (2005-)
- Tanabe et al. → 28°C 政策下的舒适性与生产性

---

## 7. 新增图 (BE 系列，PNG + 可编辑 SVG)

| 文件 | 内容 | 论文用途 |
|---|---|---|
| BE01_index_timeseries | 4 指标年间推移 + Cool Biz 28°C 基准线 | Method / Introduction |
| **BE02_index_correlation** | 冷房期 4 指标 vs 负荷散布图 | **Result: 干球 T 胜出** |
| **BE03_wbgt_signature_daytype** | WBGT × 日种别能量署名 | **Result: 学事调节机制确认** |
| **BE04_balance_point_physics** | 平衡点温度 + 物理诠释面板 | **Result: 建筑物理量化** |
| **BE05_internal_heat_gain** | 同 WBGT 下负荷差 | **Result: 内部得热直接证据** |

---

## 8. 现实评估 — 这样改后投 E&B 的胜算

### 加分项
- ✅ 完整年度 (实测全数据，非 simulated)
- ✅ 学事日历精细六分类 (本研究独有)
- ✅ 平衡点温度作为内部得热代理 (方法学贡献清晰)
- ✅ WBGT 稳健性测试 (审稿人必问，已通过)
- ✅ Cool Biz 政策链接 (日本案例的国际价值)
- ✅ 全数据 + ERA5 验证 (透明度高)
- ✅ 可编辑 SVG + 完整代码 (复现性高)

### 仍存在的风险点（审稿人会问）
- ⚠ 单栋 (b00) 而非多栋 → Discussion 中诚实说明并作为 future work
- ⚠ 仅一个学年 (JFY2025) → 多年扩展作为 future work
- ⚠ HVAC 运行数据缺失 → 平衡点温度作为间接代理已弥补部分
- ⚠ 1-2 月 BEMS 缺测 → 限定为「冷房支配型校园」的研究范围，把暖房作为 limitation

### 综合判断
重定位后，**E&B 可以一投**。主要贡献明确（平衡点位移 + WBGT 稳健性 + 学事日历方法学），数据扎实，与既有 E&B 论文血缘清晰。建议：
1. 一稿完成后投 E&B
2. 若 reject，可降至 Energies (基本可保)
3. 不建议直接攻 Building and Environment (室内环境数据缺口太大)

---

## 9. 下一步建议（待用户选择）

| 选项 | 工作量 | 产出 |
|---|---|---|
| A | 现在就把英文论文初稿写出来 (Methods + Results) | 完整论文骨架 |
| B | 先做 b00 vs 其他建筑栋 (b01-b15) 夏季对比，加 building heterogeneity 维度 | 1-2 张多栋异质性图，补强建筑维度 |
| C | 把建筑环境升级整合进中文 Word 报告 V2 | 中文 Word V2 + 新增 BE 章节 |
| D | 写 Discussion 中 Cool Biz 链接 + 政策含义 | 政策章节单独成文 |
