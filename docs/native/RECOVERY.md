# 恢复、风险与 Gate / Recovery, risk and gates

## 当前结论 / Current conclusion

**R7 是用户授权范围内生成的实验候选；正式 Canary 状态仍为 NOT_READY。** 公开源码和生成器没有新增刷机授权，也没有证明可靠恢复路径。

**R7 is an authorized experimental candidate; formal Canary readiness remains NOT_READY.** Publishing source and reproduction tools does not establish reliable recovery or device acceptance.

项目没有经验证的“主程序损坏后仍可进升级模式”证据，也没有可验证的 bootloader 备份、SWD 恢复流程或官方失败恢复说明。常规 G3 能识别设备、能发送官方固件，并不等于每一种失败后都能刷回。

Normal G3 recognition and firmware transfer do not guarantee recovery after every failure. A validated bootloader backup, SWD recovery procedure, authoritative failed-update instructions and proof of entry after main-application failure are not established in this project.

## 三种不同的恢复 / Three meanings of recovery

| 事项 / Item | 已知状态 / Status |
|---|---|
| 文件逆变换 / Inverse file transformation | CONFIRMED：精确 R7 可重建与原件 SHA 相同的文件 / Exact R7 can reconstruct the exact original file |
| 正常设备重刷原件 / Reinstall on a functioning device | 需要设备仍可被升级器接受；本次未操作 / Depends on accessible updater state; not performed in publication |
| 升级中断或程序损坏后的救回 / Recovery after interruption or corruption | UNKNOWN：未建立通用可重复流程 / No generally reproducible recovery process established |

辅助固件块的存在不证明它负责主 MCU 救援。完整文件 SHA 也不是厂商签名或设备兼容性认证。

An auxiliary executable is not proof of a main-MCU recovery mechanism. A complete file hash is not a vendor signature or device compatibility certificate.

## Gate 定义与当前状态 / Gate definitions and status

项目早期提出了九步逆向顺序，后续风险评审又用 Gate 6–9 标识完整性、恢复、HIL 与实验交付。下面沿用**后续风险 Gate 定义**，避免把同一编号的不同含义混写。Gate 1–5 的静态/离线证据不自动代表实机通过。

The initial request used a nine-step reverse-engineering plan. Later risk reviews reused Gates 6–9 for integrity, recovery, HIL and experimental delivery. The table follows the **later risk-gate definitions**; early static/offline evidence is not hardware approval.

| Gate | 当前状态 / State | 依据与缺口 / Evidence and gap |
|---|---|---|
| 1–5：格式、架构、输入与调整路径、状态 / Format, architecture, handlers, adjusters, state | Strong static and bounded evidence | 精确样本、原函数与状态限制已建立；器件型号及完整验证机制仍非全部确认 / Exact-image evidence, with remaining hardware unknowns |
| 6：设备完整性 / Device integrity | **BLOCKED** | 主向量和辅助区保留、全文件可复现；V100 设备端校验/签名机制不明 / Reproducibility is established, device verifier is not |
| 7：恢复 / Recovery | **BLOCKED** | 未证实损坏主应用后可靠进入升级/恢复 / Reliable recovery after main-application failure not established |
| 8：HIL / Hardware in the loop | **PARTIAL** | 有开发过程用户反馈，无完整 R7 光学、时序、热和长稳证据 / Development feedback, incomplete R7 physical validation |
| 9：实验文件交付 / Experimental artifact | User-authorized experimental generation | 可在本地复现；不提升为正式 Canary 通过 / Reproducible local candidate, not formal Canary approval |

总体刷写/失效恢复风险目前不能可靠量化，记为 **UNKNOWN**。不得将离线通过、用户愿意实验或原件可重建改写成 LOW。

Overall flashing/recovery risk cannot be reliably quantified and remains **UNKNOWN**. Offline passes, willingness to experiment and file reversibility do not justify a LOW rating.

## 下一步需要的证据 / Evidence needed next

在另行安排硬件工作时，应先确认具体候选 SHA 和原件，记录升级入口与失败恢复机制，然后对普通非 HSS 路径分别测 TEST、相机快门、RX 触发，以及主灯 OFF / SUB ON。同步时序与光量需要真实测量；模拟请求记录不能替代这些测量。

Any separately arranged hardware work should identify the exact candidate and original, establish update/recovery entry behavior, and measure TEST, camera shutter, RX triggering and main-OFF/SUB-ON as separate normal non-HSS cases. Synchronization and light output require physical measurements, not simulated trigger counts.

本仓库不提供一键刷机、连接升级软件或写硬件接口。工具只创建文件。

This repository provides no one-click flashing, updater control or hardware-writing endpoint. Its tools create files only.
