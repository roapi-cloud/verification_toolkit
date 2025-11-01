# 批量验证工作流规划

本文档描述计划在 `src/` 目录下新增的批量验证工作流，以支撑多个 Issue 的自动化评测，并为后续参加 SWE-bench 等解题评测提供基础设施。内容涵盖目标、系统架构、模块职责、数据流以及实施步骤。

## 1. 目标与使用场景

- **批量化执行**：从清单（手动或数据集，如 SWE-bench）批量获取 Issue，自动完成克隆、准备、执行、收集结果。
- **复用现有能力**：拆分出的 `verification_toolkit` 负责单个 Issue 的准备与执行；新工作流在其之上做编排和状态管理。
- **多运行时支持**：兼容本地执行（GitHub Issue）与 SWEREX/SWE-bench 容器环境，保留 `swerex_utils.py` 中的容器管理能力。
- **可扩展**：允许配置并行度、重试策略、自定义 Agent、结果上报（文件/数据库/仪表板）。
- **比赛需求**：输出满足官方评测格式的日志和补丁，便于提交/复现。

## 2. 拟定系统架构

```
+------------------------------+
| BatchWorkflowRunner          |
|  - load_runbook()            |
|  - schedule_jobs()           |
|  - emit_report()             |
+------------+-----------------+
             |
             v
    +-----------------+
    | JobOrchestrator |
    |  - prepare_ctx  |
    |  - run_agent    |
    |  - collect_art  |
    +---+----------+--+
        |          |
        v          v
+-----------+  +-----------+
| Context   |  | Execution |
| Provider  |  | Backend   |
+-----------+  +-----------+
            (GitHubIssuePreparer / SWE-REX)
```

### 核心组件

1. **BatchWorkflowRunner（入口）**
   - 读取批量配置（YAML/JSON/CLI）
   - 组织并发执行，协调队列/线程池/协程。
   - 汇总结果，生成报告文件。

2. **JobOrchestrator（单个任务管线）**
   - 选取合适的上下文提供者：
     - GitHub Issue → 使用 `GitHubIssuePreparer`。
     - SWE-bench 实例 → 调用 `load_swe_instance_for_swerex`。
   - 调用代理（默认 DemoVerificationAgent，支持自定义注册机制）。
   - 收集产物（补丁、日志、指标），存储到指定目录。

3. **Context Providers**
   - `GitHubContextProvider`: 封装工具包中的 `GitHubIssuePreparer`。
   - `SwerexContextProvider`: 调用 `swerex_utils` 启动容器、挂载目录，并暴露统一的 `RepositoryContext`。

4. **Execution Backends**
   - `LocalExecutionBackend`: 在宿主机执行命令（默认）。
   - `SwerexExecutionBackend`: 在容器内执行命令，封装 BashAction 调度。

5. **Result Store / Reporter**
   - 结构化输出（JSON/CSV）
   - 补丁导出（git diff）
   - 运行日志 & 命令输出

## 3. 数据流与配置

1. **输入 runbook**
   - 支持 YAML/JSON
   - 字段示例：
     ```yaml
     jobs:
       - id: gh-1
         type: github
         issue_url: https://github.com/octocat/Hello-World/issues/1
         agent: demo
       - id: swe-123
         type: swerex
         instance_id: numpy__numpy-1776
         checkout_commit: abc123
         agent: swe_solver
     max_parallel: 4
     output_dir: ./runs/2025-competition
     ```

2. **任务执行步骤**
   - 读取配置 → 生产任务队列
   - 为每个任务选择上下文提供者
   - 调用 `prepare()` 获取 `RepositoryContext`
   - 调用指定 Agent 的 `run_verification`
   - 收集返回的 `EvaluationResult` + 产物
   - 将结果写入输出目录，并聚合主报告

3. **报告格式**
   - `summary.json`: 包含每个任务的 `success`, `details`, `artifacts`
   - `patches/ID.diff`: 来自 `git diff`
   - `logs/ID.log`: Agent 执行过程日志
   - （可选）`metrics.csv`: 统计成功率、耗时等

## 4. 待实现模块清单

| 模块路径                             | 职责说明 |
|--------------------------------------|----------|
| `src/batch_workflow/__init__.py`     | 包初始化，暴露主要入口 |
| `src/batch_workflow/config.py`       | Runbook 数据模型 & 加载函数 |
| `src/batch_workflow/context/github.py` | 封装 GitHub 预处理逻辑 |
| `src/batch_workflow/context/swerex.py` | 复用 `swerex_utils`，统一接口 |
| `src/batch_workflow/agents/registry.py` | 管理 Agent 注册、工厂方法 |
| `src/batch_workflow/executor.py`     | JobOrchestrator 实现 |
| `src/batch_workflow/runner.py`       | BatchWorkflowRunner |
| `src/batch_workflow/report.py`       | 结果汇总与导出 |
| `scripts/run_batch_workflow.py`      | CLI 入口 |
| `tests/batch_workflow/`              | 单元测试与集成测试 |

## 5. 关键设计考量

- **并发策略**：建议优先采用 `asyncio` 或 `concurrent.futures` 管理 I/O 密集型任务；容器场景需限制并发度防止资源争用。
- **错误恢复**：任务级别的重试机制（如 `max_retries`），失败记录进入报告但不阻塞整个批次。
- **资源清理**：容器任务结束后释放 Docker 资源；本地任务保留或清理缓存可配置。
- **安全与凭证**：GitHub Token、容器凭证通过环境变量或配置注入；避免在日志中泄漏。
- **可观测性**：集成结构化日志与进度条（例如 `rich`），方便长时间运行时的监控。
- **扩展点**：
  - 自定义 Agent（不同策略/模型）
  - 自定义 Result Sink（数据库、远程 API）
  - 针对比赛需求的额外输出（如官方提交格式）

## 6. 实施阶段计划

1. **阶段一：框架搭建** ✅ 已完成
   - ✅ 创建 `batch_workflow` 包及核心数据模型
   - ✅ 实现配置读取、本地 GitHub context provider
   - ✅ 实现串行执行 pipeline + demo agent 适配
   - ✅ 实现并行执行支持
   - ✅ 实现结果报告和汇总
   - ✅ 编写单元测试
   - ✅ 创建 CLI 工具和示例
   - ✅ **移动到 verification_toolkit 包中，实现与 Lingxi 的分离**

2. **阶段二：容器支持与并发** 🔄 进行中
   - 🔄 对接 `swerex_utils`，抽象成统一接口
   - ✅ 引入并发执行策略，处理资源控制
   - 🔄 增加补丁导出与日志收集

3. **阶段三：稳健性与集成**
   - 增加重试、监控、指标收集
   - 编写端到端测试与性能验证
   - 产出示例 runbook、CLI 帮助以及比赛提交模板

## 7. 后续工作

- 依据该规划开始创建 `batch_workflow` 目录与骨架代码。
- 设计测试策略（mock GitHub/SWEREX，或提供最小可复现数据集）。
- 与团队确认比赛所需的额外产出（如评估脚本、评分格式），在实现阶段同步落地。

---

> 文档将随着实现进度迭代更新，建议在每个阶段开始前检查并完善需求细节。
