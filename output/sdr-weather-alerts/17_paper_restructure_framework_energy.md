# 论文重构框架 — 面向 Energy 期刊
## 从「校园负荷预测 + 削峰实践」到「低数据需求的校园负荷温度响应与容量风险识别框架」

**文档版本**: v1 (框架阶段，非全文)
**日期**: 2026-05-21
**目标期刊方向**: Energy / Energy and Buildings / Applied Energy（building energy · campus energy management · demand-side management · climate-sensitive electricity demand）
**严格数据边界**: 仅 ① 全年小时级电力；② AMeDAS 有限气象（**气温、降水、风速、风向**）；③ 完整校历；④ 合同容量。**正文实证不使用** 湿度、露点、湿球、日照、辐射、云量、HVAC 运行规则。

---

## ⚠️ 0. 一个必须先讲清的策略判断：两条研究线要分家

本会话此前的大量工作（ERA5 富气象、JMA 预报驱动、LightGBM 日前预测、CCRI 预警配信、PCA、湿度相关性）属于**另一条线**。为避免本论文自相矛盾、并守住您声明的数据边界，建议明确切分：

| | **Track A（演示/系统线）** | **Track B（本论文，Energy 投稿）** |
|---|---|---|
| 故事 | 日前峰值预测 → CCRI → Soft DR 预警配信系统 | 低数据下的温度响应 × 制度日历调节 × 容量风险识别 |
| 气象数据 | ERA5 + JMA 预报（富气象：湿度/辐射/云量） | **仅 AMeDAS 气温/降水/风速/风向** |
| 核心方法 | 机器学习预测 + 预警阈值 | 变点/分段回归 + 校历交互 + 容量风险映射 |
| 学术卖点 | 工程系统集成 | **机制解释 + 低数据框架 + 理论重定位** |
| 产物 | 日语 PPT / 预警系统原型 | Energy 期刊论文 |

**为什么必须分家**：Energy 审稿人会立刻质疑「你既然有 ERA5 湿度/辐射，为何说自己是 low-data？」。把 Track A 的富气象成果放进本文，会直接摧毁 low-data 这一核心卖点。**Track A 的 ML/预测/CCRI 在本文中最多作为「稳健性 / 未来工作」一笔带过，不进入核心实证。**

**一个有用的桥**：此前的「湿度负相关其实是气温混杂（confounding）」诊断，**恰好为本文的低数据定位提供合法性论证** —— 在校园总表（aggregate）尺度，湿度的双变量信号大部分被气温吸收，温度 + 校历是更稳定的解释变量。这可作为**文献综述/局限性中的概念性论证**（不作为本文实证变量），把「缺湿度」从短板转为「parsimony 的合理性」。

---

## 1. 新的论文定位说明（实践型预测论文 → Energy 级学术论文）

### 1.1 原稿的问题（为什么现在不够 Energy 级）

原稿主线「高温季小时级负荷预测 → 容量风险识别 → Soft DR 情景评估」存在三个学术性短板：

1. **以预测精度为中心**。MAE/RMSE/MAPE/R² 是工程指标，不是学术问题。审稿人会问「So what? 机制是什么？管理含义是什么？」
2. **把校历当控制变量**，而非研究对象。校历只是被「喂进模型」，没有被「研究」。
3. **Soft DR 情景评估缺乏数据支撑**（无 HVAC 运行数据），容易被指为「假设驱动的模拟」。

### 1.2 重定位的核心命题

> **大学校园不是单体建筑，也不是一般商业建筑，而是一个由「温度暴露 + 制度日历 + 合同容量边界」三者共同塑造的、被制度时间表调度的公共建筑群能源系统（institutionally-scheduled public building cluster）。**

本文的创新**不是更复杂的预测模型**，而是：

> **在「有限气象数据但完整制度日历可得」这一真实而普遍的约束下，构建一个低数据需求、可解释、可向管理转译的框架，用以识别（i）校园负荷的温度响应阈值与敏感性，（ii）制度日历对温度-负荷关系的调节作用，（iii）温度与制度状态如何共同形成合同容量风险。**

### 1.3 从「工程报告」到「学术论文」的三个升维动作

| 升维 | 原稿（实践） | 重构（学术） |
|---|---|---|
| 研究对象 | 「预测负荷」 | 「**解释负荷的形成机制**」：温度响应函数 + 校历调节 |
| 核心方法论 | ML 模型竞赛 | **校历状态条件下的能量签名（calendar-conditioned energy signature）** —— 一个可命名的方法贡献 |
| 终点 | 误差指标 + SDR 模拟 | **(温度 × 校历) 二维空间上的容量风险集中度**，并诚实转译为管理窗口 |

---

## 2. 新标题建议（中英各 3 个）

### English

1. **Calendar-modulated temperature sensitivity of campus electricity load and contract-capacity risk: a low-data framework**
   （主推：直接点出三个核心 —— 校历调节、温度敏感性、合同容量风险、低数据）
2. **Weather-normalized load profiling and capacity-risk identification for a university campus under limited meteorological data**
   （稳健：强调 weather normalization 与 low-data，贴 Energy and Buildings 传统）
3. **When does a campus draw critical power? Institutional-calendar and temperature drivers of capacity risk with parsimonious weather inputs**
   （问题导向，吸引力强，适合 Applied Energy 风格）

### 中文

1. **有限气象数据下大学校园电力负荷的温度响应、制度日历调节与合同容量风险识别框架**
2. **制度日历调节的校园电力温度敏感性与合同容量风险：一个低数据需求框架**
3. **气温暴露与校历状态共同驱动的大学校园容量风险：基于有限气象数据的可解释分析**

> 关键词建议（6–8）: campus energy management; weather normalization; temperature-sensitive load; institutional calendar; energy signature; contract capacity risk; demand-side management; low-data framework.

---

## 3. 重构后的研究问题与贡献点

### 3.1 研究问题（RQ）

| RQ | 表述 | 对应方法 | 对应结果节 |
|---|---|---|---|
| **RQ1** | 校园全年小时级负荷在不同制度日历状态下呈现怎样的周期结构与运行模式？ | 描述性 profiling（heatmap / boxplot / LDC） | 4.1 |
| **RQ2** | 仅用气温、降水、风速、风向，能否识别校园负荷的制冷/采暖温度阈值与敏感性？ | 变点 / 分段回归 / GAM | 4.2 |
| **RQ3** | 制度日历是否调节温度-负荷关系？同样高温下，上课日/考试期/假期/周末/活动日的响应是否不同？ | **校历状态条件下的分段回归 + ML 交互（SHAP/ALE）** | 4.3 |
| **RQ4** | 温度暴露与制度状态如何共同形成合同容量风险？哪些月/周/小时/校历状态是管理关键窗口？ | 负荷-容量比 + 风险分级 + (温度×校历) 风险面 | 4.5–4.6 |

辅助问题（作为「诚实发现」）：降水、风速、风向在校园总表尺度是否有边际贡献？（4.4）

### 3.2 三层贡献（Discussion 主线）

1. **理论贡献（Theoretical）**：将大学校园重新概念化为「温度暴露 × 制度日历」共同塑造、受合同容量约束的**被调度的公共建筑群能源系统**。提出**「制度日历调节的温度敏感性」（calendar-modulated temperature sensitivity）** 作为一个可检验的现象，并证明其存在。
2. **方法论贡献（Methodological）**：提出**低数据需求的校园负荷分析框架** —— 在无湿度/辐射/云量/HVAC 数据下，仅用气温 + 校历 + 合同容量，即可完成「温度响应识别 → 加权归一化分解 → 容量风险映射」。核心可命名构件是**「校历状态条件下的能量签名」（calendar-conditioned energy signature）**。
3. **实践贡献（Practical）**：该框架契合真实校园管理 —— 管理者通常更易获得校历、合同容量与基础气象，而非完整微气候或设备级数据。产出**容量风险筛查窗口**（哪些校历状态 × 温度区间最需要关注），可直接支持容量管理与（人因介入的）需求侧措施判断。

### 3.3 明确的边界声明（避免过度宣称）

- 不宣称解释全部气候因素（湿度/辐射缺失，承认为局限）。
- 不宣称可直接优化 HVAC（无设备数据）。
- 不宣称结果可无条件外推至所有校园（单校、单合同、特定气候带）。
- Soft DR **不写成已实地验证的控制策略**，只作为「框架可转译的管理含义」。

---

## 4. 文献综述结构（4 节 + 每节要证明的 gap + 已核实文献）

> 下列文献均已通过检索核实存在；标 ★ 为已确认作者/年份/期刊，标 ⚠ 为需在定稿前再核对具体卷期页。**请勿在未二次核对前直接引用页码。**

### 2.1 Building and campus electricity load forecasting（铺垫：成熟但以精度为中心）

**要证明的 gap**：方法已成熟（统计/ML/DL + 天气变量提升精度），但**多数停留在精度指标，缺少对负荷形成机制与管理意义的解释**。

- ★ Deb, Zhang, Yang, Lee, Shah (2017). *A review on time series forecasting techniques for building energy consumption.* Renewable and Sustainable Energy Reviews, 74, 902–924. DOI:10.1016/j.rser.2017.02.085 —— 综述锚点，证明「时序/ML 方法成熟」。
- ★ Bourdeau, Zhai, Nefzaoui, Guo, Chatellier (2019). *Modeling and forecasting building energy consumption: A review of data-driven techniques.* Sustainable Cities and Society, 48, 101533. —— 综述锚点，证明「data-driven 已成主流」。
- ★ Amber et al. (2015). *Electricity consumption forecasting models for administration buildings of the UK higher education sector.* Energy and Buildings. —— 校园/高校建筑案例。
- ★ Amber et al. (2017). *Energy Consumption Forecasting for University Sector Buildings.* Energies, 10(10), 1579. ⚠ 卷期已确认，建议核对作者全名。
- ★ Ruiz-Abellón, Gabaldón, Guillamón (2018). *Load Forecasting for a Campus University Using Ensemble Methods Based on Regression Trees.* Energies, 11(8), 2038. —— 校园 + 树模型 + 日历变量重要性。
- ⚠ Democritus University of Thrace 校园负荷剖面研究（campus load profiles 案例，建议补全引用）。

**收尾句式（gap 引出）**：> "尽管预测精度持续提升，这些研究将气象与日历变量主要作为提高 R²/降低 MAPE 的输入，**很少把负荷的形成机制本身作为研究对象**，也很少把模型输出转译为容量管理决策。"

### 2.2 Weather normalization, temperature response, and energy signature（核心方法谱系）

**要证明的 gap**：即使只有干球温度，变点/度日/能量签名方法也能稳健识别基础负荷、制冷敏感负荷、采暖敏感负荷 —— **这正是「低数据」可行的理论依据**；但这些方法**通常把校历当噪声/控制变量，而非调节因子**。

- ★ ASHRAE RP-1050 / Inverse Modeling Toolkit（Kissock, Haberl, Claridge, ~2003）；ASHRAE Guideline 14 —— 变点/度日逆模型的方法权威来源。
- ★ Paulus & Kissock — *Change Point and Degree Day Baseline Regression Models in Industrial Facilities.* —— 变点 + 度日基线回归。
- ⚠ 变量基度日（variable-base degree-day, VBDD）与 3P/4P/5P change-point 模型族（建议引 ASHRAE 14 与 IMT 原始文献）。
- ★ 分段回归识别逐时 CDH/HDH 参考温度的研究（hourly segmented regression，见 arXiv:2109.00643 / PMC9450160「Using temperature sensitivity to estimate shiftable electricity demand」）。

**收尾句式**：> "能量签名与变点模型证明，仅凭干球温度即可稳健分离基础负荷与温度敏感负荷；然而既有应用**默认温度响应在不同运行状态下同质**，鲜少检验制度日历对响应斜率与阈值的调节。"

### 2.3 Institutional calendar, occupancy, and schedule effects in campus energy use（把校历升为理论贡献）

**要证明的 gap**：校历显著影响校园负荷（已有证据），但**多数研究将其作为预测特征或占用代理，未系统刻画其对「温度-负荷关系」的调节，也未连接到容量风险**。

- ★ *Reducing university energy use beyond energy retrofitting: The academic calendar impacts.* Energy and Buildings (2021), S0378778820334332 —— **关键文献**：证明学历调整可显著改变校园能耗（量级证据）。
- ★ 占用驱动的校园建筑用电预测（*An occupancy-based model … three campus buildings in Tianjin*, Energy and Buildings 2020, S0378778819317712）。
- ★ *Classification of daily electric load profiles of non-residential buildings*, Energy and Buildings (2020) —— 非住宅负荷剖面分类，呼应 RQ1。
- ⚠ 含校历/时刻表指标的高校负荷预测（如 hybrid SARIMAX–LSTM with academic calendar，6 年数据案例，见 ScienceDirect S0378778825011302）。

**收尾句式**：> "现有研究确认校历影响校园用电，但多将其作为占用代理或预测特征；**校历作为「温度敏感性的调节变量」这一角色尚未被系统刻画**，其对合同容量风险的放大机制更未被量化。本文将校历从控制变量提升为研究对象。"

### 2.4 Capacity-risk translation and low-data energy management（落脚：从指标到管理）

**要证明的 gap**：预测/解释最终需转译为**合同容量风险、峰值暴露、管理窗口**，但多数研究止步于误差指标；同时，**真实校园管理常面临气象数据不完整**，需要低数据、可解释、可落地的框架。

- ★ *Review of peak load management strategies in commercial buildings.* Renewable and Sustainable Energy Reviews (2021), S2210670721007599 —— 峰值管理综述。
- ⚠ 需求侧管理 / 需求响应分类（price-based vs incentive-based）综述（建议引一篇 DR review 锚点）。
- ⚠ 建筑能源灵活性（energy flexibility）综述（如 Annex 67 相关，建议核实后引用）。
- ⚠ 合同容量 / 契约电力 / demand charge 相关研究（日本/东亚电价结构语境，建议补 1–2 篇本地化文献）。

**收尾句式**：> "峰值与需求侧管理研究丰富，但**容量风险的『形成结构』—— 即风险在温度与制度状态空间中的集中位置 —— 很少被显式刻画**；且多数方法依赖丰富数据，与真实校园低数据场景错配。本文填补这一缺口。"

### 2.5 文献综述的总 gap 陈述（四节收束）

> 综上，三个具体空白：(1) 预测精度导向研究**未解释负荷形成机制与管理含义**；(2) 气象敏感性方法**默认温度响应同质、未刻画制度日历的调节**；(3) 校园能源研究**将校历当控制变量、未连接容量风险，且多依赖丰富气象数据**。本文以「低数据 + 完整校历 + 合同容量」回应：**是否能构建一个可解释、低数据需求的校园负荷响应与容量风险识别框架，并揭示制度日历对温度敏感性的调节及其容量风险后果？**

---

## 5. 概念框架（Conceptual Framework，文字版变量关系）

### 5.1 核心因果叙事

```
[输入层 / 约束]
  有限气象数据   E = { 气温 T, 降水 P, 风速 W, 风向 D(sin/cos) }
  制度日历状态   S = { 上课日, 考试期, 假期, 周末, 节假日, 活动日 }
  容量边界       C = 合同容量 (常数/分段)
        │
        ▼
[环节①  负荷剖面刻画]  Load profiling
  L(t) 在 (月 × 小时)、(星期 × 小时)、校历状态 上的周期结构
  → 回答 RQ1：制度性运行模式
        │
        ▼
[环节②  校历调节的温度响应]  Calendar-modulated temperature response
  对每个校历状态 s ∈ S，估计分段/变点温度响应函数：
     L | (T, s) = baseload(s) + β_cool(s)·CDH(T;τ_c(s)) + β_heat(s)·HDH(T;τ_h(s))
  关键对象：阈值 τ_c(s), τ_h(s) 与敏感斜率 β(s) 随校历状态变化
  → 回答 RQ2（阈值/敏感性）与 RQ3（校历调节）
        │
        ▼
[环节③  加权归一化负荷分解]  Weather-normalized decomposition
  L(t) = B(t) + Q(t) + R(t)
     B(t) = institutional baseline load   ← 小时/星期/月/校历状态解释
     Q(t) = temperature-sensitive load    ← 由②的阈值与度时解释
     R(t) = unexplained residual          ← 识别异常日/活动叠加
  → 低数据可解释分解
        │
        ▼
[环节④  容量风险暴露映射]  Capacity-risk exposure
  ρ(t) = L(t) / C   （负荷-容量比）
  风险分级 Normal / Watch / High / Critical
  指标：exposure hours, high-risk duration, critical events,
        风险在 (月, 小时, 星期, 校历状态, 温度区间) 上的集中度
  关键产物：在 (温度 × 校历状态) 二维空间上的风险面
  → 回答 RQ4
        │
        ▼
[环节⑤  低数据校园能源管理转译]  Low-data management translation
  容量风险筛查窗口 = f(校历状态, 温度区间, 时段)
  诚实的轻量反事实：同温下「上课日 vs 假期」风险差、去极端高温后的归一化风险、
  高温活动日的风险增量 —— 均不模拟具体 HVAC 控制
  → 管理含义（人因介入的需求侧判断），非自动控制
```

### 5.2 一句话框架命题

> **Limited weather data + institutional calendar + capacity boundary → (calendar-modulated) load-response profiling → weather-normalized load decomposition → capacity-risk exposure → low-data campus energy management.**

### 5.3 框架的「新对象」是什么（novelty 的落点）

整篇论文的**新分析对象**是：**温度响应函数随制度日历状态的变化**，以及由此在 **(温度 × 校历) 空间**上形成的**容量风险集中结构**。这两个对象在既有文献中均未被显式刻画 —— 这是 novelty 的可辩护落点。

---

## 6. 新的 IMRaD 详细大纲

### 1. Introduction（重写）
- 1.1 气候变暖与极端高温 → 公共机构电力负荷与容量风险上升。
- 1.2 大学校园 = 受制度时间表调度的公共建筑群；负荷受气象 **与** 教学/考试/假期/活动制度时间共同塑造。
- 1.3 既有校园负荷研究多关注预测精度，**少解释温度暴露与制度日历如何共同形成容量风险**。
- 1.4 真实校园管理常面临**气象数据不完整** → 需要低数据、可解释、可落地框架。
- 1.5 本文基于「全年小时负荷 + 有限 AMeDAS 气象 + 完整校历 + 合同容量」，提出 weather-normalized campus load profiling and capacity-risk identification framework。
- 1.6 贡献声明（理论/方法/实践三点）+ 论文结构。

### 2. Literature Review（见第 4 节四小节）
- 2.1 Building & campus load forecasting（精度导向之不足）
- 2.2 Weather normalization / change-point / energy signature（低数据可行的理论依据）
- 2.3 Institutional calendar & schedule effects（把校历升为研究对象）
- 2.4 Capacity-risk translation & low-data management（落脚管理）
- 2.5 总 gap 陈述

### 3. Methodology
- 3.1 Data description（含**明确缺失变量声明**：湿度/辐射/云量/HVAC 不可用）
- 3.2 Feature construction
  - 气象：dry-bulb T、precip、wind speed、wind dir(sin/cos)、温度滞后(1/3/6/24h)、滚动温度暴露、CDH/HDH
  - 日历：hour、dow、month/season、weekend、holiday、class day、exam、vacation、event day
- 3.3 Descriptive profiling（heatmap / boxplot / load duration curve）
- 3.4 Temperature response modeling（分段/变点回归 + GAM；识别 comfort range / cooling & heating threshold / marginal sensitivity / **calendar-specific response**）
- 3.5 ML as robustness & interaction（LightGBM/XGBoost **仅作**变量重要性、非线性、SHAP/ALE 温度×校历交互；**明示非创新核心**）
- 3.6 Weather-normalized load decomposition（L = baseline + temperature-sensitive + residual）
- 3.7 Capacity-risk identification（ρ=L/C、风险分级、exposure hours、risk concentration、(温度×校历) 风险面）
- 3.8 Scenario / light counterfactual（**诚实、无 HVAC 规则**：同温下 class vs vacation 风险差；去极端高温后的归一化风险；高温活动日风险增量）

### 4. Results
- 4.1 Annual campus load profile and institutional calendar pattern（RQ1）
- 4.2 Temperature-load response and seasonal thresholds（RQ2）
- 4.3 Calendar-modulated temperature sensitivity（RQ3，**核心结果**）
- 4.4 Role of limited weather variables（降水/风速/风向边际贡献 —— 弱也是发现：总表尺度温度+校历更稳定）
- 4.5 Weather-normalized load decomposition（基础/温度敏感/异常残差）
- 4.6 Capacity-risk exposure under temperature–calendar interaction（RQ4，**核心结果**）

### 5. Discussion
- 5.1 Theoretical contribution（校园 = 温度×制度共塑的建筑群；calendar-modulated temperature sensitivity 存在）
- 5.2 Methodological contribution（低数据框架；calendar-conditioned energy signature）
- 5.3 Practical contribution（契合真实管理；容量风险筛查窗口；人因介入的 DSM）
- 5.4 Limitations（缺湿度/辐射/云量/HVAC；单校单年单气候带；SDR 非实地验证）+ 把湿度混杂的概念性论证放此处
- 5.5 Future work（多年/多校；引入富气象做对照；Track A 的预报-预警系统）

### 6. Conclusion（回答四个 RQ，重申三层贡献与边界）

### 图表清单（建议，全部可由现有 AMeDAS+校历+负荷数据生成）
- F1 概念框架图
- F2 (月×小时)、(星期×小时) 负荷 heatmap
- F3 校历状态分组 boxplot + load duration curve
- F4 温度-负荷散点 + 分段/变点拟合（全样本）
- F5 **校历状态分层的温度响应曲线**（核心）
- F6 SHAP/ALE：温度 × 校历交互
- F7 负荷分解（baseline / temp-sensitive / residual）时间序列
- F8 ρ=L/C 风险分级时序 + 风险小时分布
- F9 **(温度区间 × 校历状态) 风险集中热力图（核心）**
- T1 数据与变量表（含缺失声明）；T2 各校历状态阈值/斜率表；T3 容量风险统计表

---

## 7. 原稿处置（保留 / 降级 / 删除 / 重写）

| 原稿成分 | 处置 | 说明 |
|---|---|---|
| 全年小时负荷数据 | **保留（升级为主角）** | 从「被预测对象」升为「被解释机制」 |
| 完整校历数据 | **保留 + 升级** | 从控制变量升为研究对象（RQ3 核心） |
| 合同容量 | **保留 + 升级** | 容量风险映射的基准 C（RQ4 核心） |
| 描述性 profiling | **保留** | 作为 4.1，服务 RQ1 |
| 容量风险指标（L/C、分级） | **保留 + 扩展** | 增加 (温度×校历) 风险面，作为 4.6 核心 |
| AMeDAS 气温 | **保留（核心气象）** | 温度响应主驱动 |
| 降水/风速/风向 | **保留（降级为边际检验）** | 4.4，弱贡献也是诚实发现 |
| LightGBM/XGBoost 预测 | **降级** | 从创新核心 → 3.5 稳健性/交互分析（SHAP/ALE） |
| MAE/RMSE/MAPE/R² | **降级** | 从头条 → 支撑性附表/稳健性 |
| Soft DR 情景评估 | **降级 + 改写** | 从「评估」→ 3.8 诚实轻量反事实 + 管理含义；**不写成已验证控制策略** |
| 「日前预测系统」框架 | **降级为 future work** | 归入 Track A，5.5 一笔带过 |
| ERA5 富气象（湿度/辐射/云量） | **删除/移出正文** | 违反数据边界；湿度混杂仅作概念性论证入 5.4 |
| WBGT / 体感温度 / 露点 | **删除** | 依赖湿度，超出边界 |
| PCA（10 气象变量） | **删除** | 依赖富气象，超出边界 |
| CCRI 预警配信系统 | **移出（归 Track A）** | 非本文（low-data 机制论文）范畴 |
| HVAC 控制模拟 | **删除** | 无设备数据，不可宣称 |
| Introduction | **重写** | 见 6.1，从机制+管理+低数据切入 |
| Literature Review | **重写** | 见第 4 节四小节结构 |
| Methodology | **重写** | 以变点/分段 + 校历交互为核心，ML 降级 |
| Results | **重写** | 服务 RQ，机制优先于精度 |
| Discussion | **重写** | 三层贡献 + 诚实边界 |

---

## 8. 下一步（待您确认后再做）

按您「先框架后全文」的要求，**本文档止于框架**。确认本框架后，建议下一步顺序：

1. **Introduction 中文重写版**（约 800–1000 字，含 gap → RQ → 贡献链）。
2. **Literature Review 中文重写版**（四小节，嵌入已核实文献 + 每节 gap 收束句）。
3. 待确认数据可用范围后（2025 全年小时负荷是否已就绪），生成 3.4/3.6/3.7 的**可复现分析脚本**与图 F4–F9。
4. 文献定稿核对（标 ⚠ 的卷期页二次核实；补 1–2 篇日本/东亚合同容量与 DSM 本地文献）。

---

## 附：已核实文献清单（核心锚点）

| 类别 | 文献 | 状态 |
|---|---|---|
| 综述 | Deb et al. 2017, *RSER* 74:902–924, DOI 10.1016/j.rser.2017.02.085 | ★ 已核实 |
| 综述 | Bourdeau et al. 2019, *Sustainable Cities and Society* 48:101533 | ★ 已核实 |
| 校园预测 | Amber et al. 2015, *Energy and Buildings*（UK higher-ed administration buildings） | ★ 已核实（核对页码） |
| 校园预测 | Amber et al. 2017, *Energies* 10(10):1579 | ★ 已核实 |
| 校园预测 | Ruiz-Abellón et al. 2018, *Energies* 11(8):2038（regression-tree ensembles, campus） | ★ 已核实 |
| 加权归一化 | ASHRAE RP-1050 / IMT（Kissock, Haberl, Claridge）; ASHRAE Guideline 14 | ★ 已核实 |
| 变点/度日 | Paulus & Kissock, *Change Point and Degree Day Baseline Regression Models* | ★ 已核实 |
| 温度响应 | hourly segmented regression CDH/HDH（arXiv:2109.00643 / PMC9450160） | ★ 已核实 |
| 校历效应 | *Reducing university energy use … The academic calendar impacts*, *Energy and Buildings* 2021 | ★ 已核实（关键） |
| 校历/占用 | occupancy-based campus model（Tianjin three buildings）, *Energy and Buildings* 2020 | ★ 已核实 |
| 负荷剖面 | *Classification of daily electric load profiles of non-residential buildings*, *Energy and Buildings* 2020 | ★ 已核实 |
| 峰值管理 | *Review of peak load management strategies in commercial buildings*, *RSER* 2021 | ★ 已核实 |
| DSM/灵活性 | DR 分类综述 + energy flexibility 综述 | ⚠ 待补具体锚点 |
| 合同容量 | 日本/东亚 demand charge / 契約電力 文献 | ⚠ 待补本地化文献 |
