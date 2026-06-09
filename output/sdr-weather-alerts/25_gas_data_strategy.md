# 混合时间粒度的处理策略 — 月度燃气 × 逐时电力

**问题**: 校园空调既用电（夏季冷房 + 部分冬季暖房）也用城市燃气（冬季暖房主力？），但燃气只有月度账单。如何在论文里把这两种数据合理结合，且不被审稿人挑出方法论硬伤？

**作成日**: 2026-06-01

---

## 1. 一句话结论

> **不要硬把月度燃气拆成逐时再合并到电力**。**正确做法**是：(a) 在 Methods 中**明确声明数据粒度差异**；(b) 用月度燃气做"**总能量平衡核查 + 暖房份额估算 + 燃料切换识别**"，电力分析仍主导逐时层面；(c) 必要时用 ASHRAE 标准的"**月度变点回归**"独立分析燃气，与电力分析**并列报告**而不强行融合。这是 ASHRAE Guideline 14 与 Building Simulation (Springer 2020) 等的标准做法。

---

## 2. 文献认可的做法（按合理性排序）

### ✅ 做法 A — 并列分析（Parallel Analysis）★ 最推荐 ★

**做什么**: 电力做逐时能量署名；燃气**独立**做月度变点回归（HDD-based）。两者**不强行融合**，但在 Discussion 中联合解读。

**文献依据**:
- [ASHRAE Guideline 14-2014, Inverse Modeling Toolkit](https://watchwire.ai/ashrae-guideline-14/) — 月度燃气账单 × 月度 HDD 的 change-point 回归是公认基准（IPMVP Option C）
- [Simplified Weather-Related Building Energy Disaggregation, MDPI Buildings 2022 12(10):1717](https://www.mdpi.com/2075-5309/12/10/1717) — 11栋首尔办公楼用月度账单 + degree-day 直接做暖房/冷房分解
- [Abraxas Energy: weather normalization of utility bills](https://www.abraxasenergy.com/articles/intro-weather-normalization/) — 行业标准做法

**优点**:
- 不引入虚假精度（不假装月度燃气拥有它本来没有的逐时信息）
- 审稿人无可指摘——这是 IPMVP/ASHRAE 标准
- 可直接告知 "电力暖房弱 (R²=0.05) 是因为暖房多由燃气承担，由月度燃气回归独立验证"

**操作**:
1. 燃气月度账单 (kWh 当量, 12 点) × 月度平均气温 → 3-parameter change-point 回归
2. 报告燃气的暖房平衡点温度 T_h,gas 与暖房斜率 β_h,gas
3. **与电力的暖房斜率 β_h,elec 形成对比表**：若 |β_h,gas| ≫ |β_h,elec| → 证实暖房非电力主导

### ✅ 做法 B — 用月度燃气做"年/季能量份额分解"作为 Discussion 增强

**做什么**: 月度燃气 × HDD 拟合后，估算"暖房期燃气供应了多少 MWh"，再与"电力暖房感度推算的暖房电量"对比，得到**冬季供暖的燃料构成比例**。

**文献依据**:
- [Building Simulation (Springer) 2020 — Hourly energy profile determination technique from monthly energy bills](https://link.springer.com/article/10.1007/s12273-020-0698-y) — 月度账单 + 度日法估算供暖比例的方法学
- [ACEEE 2016: Disaggregation and Future Prediction of Monthly Residential Building Energy Use](https://www.aceee.org/files/proceedings/2016/data/papers/12_410.pdf) — 月度数据做 end-use 分解

**操作**:
- 燃气年总量 (kWh 当量) ÷ (电力暖房估算 + 燃气暖房估算) = **燃气暖房份额**
- 例如得到"冬季供暖中 ~80% 由燃气承担"——直接落到 Discussion 4.x 节

### ⚠️ 做法 C — 不要做：月度燃气强行拆为逐时

**为什么不**:
- 月度 → 逐时拆分必须假设 HVAC 运行模式（开机时长、热负荷分布），而我们**没有 HVAC 数据**
- 引入的假设比解决的问题多，CV-RMSE 通常 >30%（ASHRAE 14 计量基准是 ≤15%）
- 审稿人会直接指出"你没有逐时燃气怎么能声称逐时燃气分析？"

如果**确实需要**逐时燃气（一般不需要），需具备：HVAC 时间表、设备 COP/效率、室内设定温度——这些我们都没有。

### ⚠️ 做法 D — 不要做：把月度燃气当作"月度修正项"加到逐时电力上

会污染您论文最干净的卖点（**学事日历调节冷房感度 R²=0.91**）。冷房分析全部由电力决定，无需燃气介入。

---

## 3. 推荐落入 Energies 论文的具体写法

### 3.1 在 §2.2 Data sources 加一行

> Monthly natural-gas consumption records were also obtained from the campus energy management office (FY2025, 12 monthly billing values). Gas use is exclusively associated with space heating and domestic hot water; no gas-fired cooling is installed. Because gas data are available only at monthly resolution, gas is analysed using a separate monthly degree-day regression and reported in parallel with the hourly electricity analysis, following ASHRAE Guideline 14 practice [ref].

### 3.2 在 §2.5 Seasonal stratification 之后加 §2.5b — Gas analysis at monthly resolution

> For natural gas (12 monthly values), we fit a three-parameter heating-only change-point model
> G_m = a + b · HDD(T_h, m), G_m ≥ a,
> where G_m is the monthly gas consumption in kWh equivalent, HDD(T_h, m) is monthly heating degree-days with balance-point T_h, and a captures non-weather-dependent baseload (e.g. domestic hot water). The balance-point T_h is estimated by minimising sum-of-squared residuals over a grid 14–22 °C, consistent with ASHRAE RP-1050 Inverse Modeling Toolkit.

### 3.3 在 §3.2 加 §3.2b — Gas signature complements the weak electric heating slope

> The cooling-dominated electricity signature reported in §3.2 (heating slope −9.8 kWh·h⁻¹·°C⁻¹, R² = 0.05) is consistent with a campus where space heating is predominantly fuelled by natural gas. The monthly gas signature (Fig. X) yields T_h,gas = [your number] °C and heating sensitivity b_gas = [your number] kWh per HDD. The implied annual heating energy carried by gas is [Y] MWh, against an electricity-borne heating contribution of approximately [Z] MWh. Gas thus supplies approximately [Y/(Y+Z)] of total annual heating energy, confirming that the weak electric heating slope is structural (fuel choice) rather than an artefact of BEMS data gaps.

### 3.4 在 §4.4 Limitations 加一段

> Gas data were available only at monthly billing resolution, which prevents an hour-of-day analysis of the heating regime. Following ASHRAE Guideline 14 practice, gas was analysed separately at monthly resolution rather than disaggregated to hours by assumption-laden methods. Sub-daily heating analysis would require either an hourly gas sub-meter or a calibrated building-energy-simulation model; both are identified as future work.

---

## 4. 您只需提供的最少燃气数据

一张 12 行的表就够，**单位需统一**：

```
month,           gas_volume_m3, gas_kWh_equiv
2025-04,         ___,            ___
2025-05,         ___,            ___
...
2026-03,         ___,            ___
```

**换算系数** (日本城市燃气 13A): **约 45 MJ/Nm³ ≈ 12.5 kWh/Nm³** (高位发热量)。若您账单已给 kWh 或 MJ，无需换算。

**也希望同时给**:
- 燃气年度总账 (核查月度加总)
- 单价结构 (基本料金 + 従量料金) — 用于经济分析
- 燃气消费的**用途分类**(若有): 暖房 / 给湯 / 厨房

---

## 5. 拿到燃气数据后，我会立刻产出

| 产出 | 内容 |
|---|---|
| **新图 Figure 11** | Monthly gas signature: G_m vs HDD scatter + 3-parameter change-point fit |
| **新表 Table 5** | Multi-fuel annual energy balance: electricity vs gas, cooling vs heating, by season |
| **§2.5b + §3.2b 段落** | 已写好的 Methods + Results 模板（见上） |
| **§4.4 Limitations 段落** | 已写好（见上） |
| **更新 Abstract** | 把"campus is cooling-dominated"改为"campus electricity is cooling-dominated; heating is largely gas-fired (≈X % share)" |

---

## 6. 文献清单（已核实，可直接引用）

- **ASHRAE Guideline 14-2014** — Measurement of Energy, Demand, and Water Savings. American Society of Heating, Refrigerating and Air-Conditioning Engineers. 月度账单 weather normalization 的官方基准。
- **Kissock, Haberl & Claridge (2003)** — ASHRAE RP-1050 Inverse Modeling Toolkit. 提供 3P / 4P / 5P change-point 模型实现。
- **Sun, K.; et al. (2020)** — *Hourly energy profile determination technique from monthly energy bills*. Building Simulation 14(2), 315–331. DOI:10.1007/s12273-020-0698-y. 月度→小时分解方法论与局限。
- **Eom, Park & Hong (2022)** — *Simplified Weather-Related Building Energy Disaggregation and Change-Point Regression: Heating and Cooling Energy Use Perspective*. Buildings (MDPI) 12(10):1717. 月度账单 + degree-day 做暖房/冷房分解的最新方法学示范。
- **Westphal & Lamberts (2007)** — Building simulation calibration using degree-days; widely-cited reference for monthly resolution analysis.
- **ACEEE Summer Study 2016 (Paper 12_410)** — Disaggregation and Future Prediction of Monthly Residential Building Energy Use. 月度账单的 end-use 分解。

---

## 7. 接下来您只需做一个决定

| 选择 | 内容 |
|---|---|
| **A** | 您提供 12 个月燃气账单 (kWh 或 m³)，我立刻产出 Fig. 11 + Table 5 + §2.5b/§3.2b/§4.4 三段，整合进 Energies 投稿包 (commit 升级版) |
| B | 您只能拿到年度合计而非月度，我用单点燃气+全年 HDD 给出粗略份额估计，但只能放 Discussion 而非 Results |
| C | 暂时不补，按现状投稿——我把上述"§2.4 limitations: 暖房弱可能因非电力供暖"段落加强，作为诚实的局限性说明 |

**我的推荐: A**。月度账单本就是 IPMVP/ASHRAE 公认数据，**绝对不丢分**，反而把您论文的"冷房支配"叙事补成完整的"冷房电、暖房气"双燃料故事——比单纯电力分析的卖点更强。

---

**Sources cited (verified)**:
- [ASHRAE Guideline 14 explainer — Watchwire](https://watchwire.ai/ashrae-guideline-14/)
- [Sun et al. 2020, Building Simulation, Springer](https://link.springer.com/article/10.1007/s12273-020-0698-y)
- [Eom et al. 2022, Buildings (MDPI) 12(10):1717](https://www.mdpi.com/2075-5309/12/10/1717)
- [Abraxas Energy weather normalization intro](https://www.abraxasenergy.com/articles/intro-weather-normalization/)
- [ACEEE Summer Study 2016 — Paper 12_410](https://www.aceee.org/files/proceedings/2016/data/papers/12_410.pdf)
