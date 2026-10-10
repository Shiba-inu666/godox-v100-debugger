# 副灯能否套用主灯 TTL / Can SU-1 reuse main-flash TTL?

## 结论 / Conclusion

**有可研究的复用途径，但不能通过复制主灯结果或改一个模式值就声称开启了真正的副灯 TTL。R7 的副灯仍是手动功率。**

**Some reuse is plausible, but copying main output or changing a mode value does not establish genuine SU-1 TTL. R7 SUB power remains manual.**

## 当前证据 / Current evidence

针对精确的 V100F V1.03 原件及 R7，执行了 [90 项有界观测](../../native/evidence/TTL_FEASIBILITY_RESULTS.json)，测试入口见 [analyze_su1_ttl.py](../../native/lab/analyze_su1_ttl.py)。这里的 CONFIRMED 仅针对模拟中实际执行的指令与给定状态，不是实测的测光结果。

The [90 bounded observations](../../native/evidence/TTL_FEASIBILITY_RESULTS.json) compare the exact original with R7. CONFIRMED here refers to executed instructions in the supplied modeled states, not physical metering measurements.

| 观察 / Observation | 含义 / Meaning |
|---|---|
| 相机 B1 预闪路径触发主灯，没有副灯预闪请求 / Camera B1 preflash requests main only | 副灯没有自动加入已覆盖的测光链 / SUB is not automatically part of the covered metering sequence |
| B6 测光输入变化可以改变主灯结果，而固定的副灯 UI 值保持固定时长 / Metering input changes main results but not a fixed SUB duration | 主、副参数来源不同 / Separate parameter sources |
| 例：输入 40 → 主灯码 90，输入 100 → 主灯码 4,500；副灯设置码 30 → 时长码 49 / Example encoded values | 这些是内部编码，不是 µs、Ws 或实测光量 / These are encoded values, not measured duration or energy units |
| RX B4/01 已覆盖预闪只请求主灯，B4/09 可以走普通双灯发光 / Covered RX preflash is main-only; normal exposure can be joint | 普通同步闪光不等于参与 TTL / Normal synchronized emission is not TTL participation |
| Sender 主灯 OFF 时没有对应的副灯预闪 / Main-OFF Sender lacks corresponding SUB preflash | 已实现副灯单独主曝光不等于副灯单独 TTL / SUB-only main exposure is not SUB-only TTL |

## 三条不同路线 / Three different routes

| 方案 / Approach | 判断 / Assessment |
|---|---|
| 副灯跟随主灯结果，按比例输出 / Scale SUB from main result | 可以研究为联动手动模式；如果副灯没有参与测光，不能叫真正 TTL / Could be linked open-loop output, not established TTL |
| 只有副灯发光，并让副灯参与预闪 / SUB-only TTL with SUB preflash | PROBABLE 研究方向：可能复用相机协议和 FEC，但需要副灯预闪、标定、就绪和主曝光验证 / Possible protocol/FEC reuse, requiring preflash, calibration, readiness and exposure validation |
| 主灯、副灯分别独立 TTL / Independently metered main and SUB | BLOCKED：没有证实两条独立测光结果通道或可靠的分次测光机制 / No established independent metering channels or sequential metering mechanism |

## 复用什么，缺什么 / Reuse and missing evidence

可以优先研究复用原相机通信、FEC 表达、曝光事件和原厂发光执行函数。不能直接沿用主灯能量标定：主灯与副灯的光学结构、功率范围和照射方向不同，主灯码值不是已经标定好的副灯能量。

Candidate reuse includes camera communication, FEC representation, exposure events and original emission routines. Main-head energy calibration cannot simply be assumed valid for a differently powered and directed SUB head.

最小的下一步是保持当前手动 R7 不变，建立独立离线原型，追踪副灯预闪准入以及相机结果如何送到副灯执行层；再在具备真实时序与光量测量条件时验证。副灯单独 TTL、双灯固定比例和两灯独立 TTL 必须分开处理，不能把三个需求混成一个开关。

The smallest next step is a separate offline prototype tracing SUB preflash eligibility and routing of camera results to SUB execution, followed by physical timing and energy measurements. SUB-only TTL, fixed-ratio dual-light output and independently metered lights must be treated as distinct requirements.

**当前功能状态：研究可以继续；副灯 TTL 实验固件生成仍为 BLOCKED。本次发布没有注入新的 TTL 代码。**

**Status: research can continue; an experimental SU-1 TTL firmware remains BLOCKED. This release injects no new TTL implementation.**
