# 金融智能审计助理 (Financial Insight AI Agent)

本项目是一款基于大语言模型（LLM）驱动的自动化金融数据分析工具。它通过原生工具调用（Tool Calling）Agent 架构将 AI 的逻辑推理能力与 Pandas 的数据处理能力相结合，旨在解决审计实务中海量流水难筛选、异常分析耗时长的痛点。

---

## 核心亮点
* **语义化审计查询**：审计人员无需编写 SQL，通过自然语言即可完成“穿行测试”和“异常识别”。
* **任意运营商 API 接入**：内置 DeepSeek、OpenAI、通义千问、智谱 GLM、月之暗面、百度文心等预设，同时支持 Claude / Anthropic 兼容端点与自定义任意 OpenAI / Anthropic 协议端点，一处配置即可切换。
* **原生工具调用驱动**：以模型原生 Tool Calling 驱动 Python 代码执行，不依赖文本格式解析，长链路分析稳定不中断；代码报错自动回传模型自我修正。
* **多维风险扫描**：基于真实金融波动逻辑，自动识别大额支出、频繁交易及预算偏离。
* **专业级可视化**：分析过程中直接通过 `st.pyplot()` 将 Matplotlib 图表渲染至页面，一键生成符合审计底稿标准的趋势图与分布图。
* **审计合规设计**：模型参数锁定 Temperature=0，确保分析过程的严谨性与结果的可追溯性。

## 技术栈
* **开发框架**：[LangChain](https://www.langchain.com/) (原生工具调用 Agent 架构)
* **前端界面**：[Streamlit](https://streamlit.io/) (响应式 Web 交互)
* **大模型引擎**：支持任意 OpenAI 兼容（DeepSeek / GPT-4o / Qwen / GLM / Kimi / 文心）与 Anthropic 兼容（Claude 系列）端点
* **数据引擎**：Pandas, NumPy, Matplotlib, Openpyxl

## 快速开始
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 启动应用
   ```bash
   streamlit run app.py
   ```
3. 在左侧侧边栏选择服务商，填入 API Key（必要时填写 Base URL 与模型名称）。
4. 上传财务报表（CSV / Excel），输入审计需求，点击「开始分析」。

> 提示：API Key 仅用于当前会话，程序不会持久化存储。

## 项目结构
```text
杨开颜_AI审计项目演示版/
├── app.py                 # 主程序：UI 布局、多协议模型初始化、工具调用 Agent 循环
├── requirements.txt       # 环境依赖
├── transform_data.py      # 数据转换脚本：生成脱敏测试数据
├── README.md              # 项目文档：即本文件
└── data/
    └── audit_test_data.xlsx # 测试数据：脱敏后的企业财务报表 (基于真实市场数据转换)
```

## 使用示例
在分析框中输入自然语言指令即可，例如：
- 「分析营收异常值，并画出月度趋势图」
- 「识别大额交易并对预算偏离进行风险扫描」
- 「计算各季度同比增速，柱状图对比」

模型会自动调用 Python 执行计算与绘图，并将图表与分析结论一并呈现在页面。
