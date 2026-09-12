import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain_openai import ChatOpenAI

# --- 1. 环境加固：解决中文乱码 ---
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 2. 页面美化 ---
st.set_page_config(page_title="智审 AI - 金融数据分析助手", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS 让界面更专业
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("Financial Insight AI Agent")
st.caption("基于 LangChain 的自动化审计与分析专家（支持任意 OpenAI 兼容 API）")
st.markdown("---")

# --- 3. 侧边栏：配置中心 ---
# 服务商预设：标注协议类型（openai / anthropic），分别用对应客户端调用
PROVIDER_PRESETS = {
    "DeepSeek（深度求索）": {
        "protocol": "openai",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "OpenAI": {
        "protocol": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "通义千问（Qwen）": {
        "protocol": "openai",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "智谱 GLM": {
        "protocol": "openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
    },
    "月之暗面（Kimi）": {
        "protocol": "openai",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
    },
    "百度文心（千帆）": {
        "protocol": "openai",
        "base_url": "https://qianfan.baidubce.com/v2",
        "model": "ernie-speed-128k",
    },
    "Claude / Anthropic 兼容（如 wenge 中转）": {
        "protocol": "anthropic",
        "base_url": "https://aicoding.wenge.com",
        "model": "deepreasoning-gl-5.2",
    },
    "自定义（OpenAI 兼容端点）": {
        "protocol": "openai",
        "base_url": "",
        "model": "",
    },
    "自定义（Anthropic 兼容端点）": {
        "protocol": "anthropic",
        "base_url": "",
        "model": "",
    },
}

with st.sidebar:
    st.header("⚙️ 系统配置")

    # 选择服务商，决定协议、默认 base_url 与模型
    provider_name = st.selectbox("选择模型服务商", list(PROVIDER_PRESETS.keys()))
    preset = PROVIDER_PRESETS[provider_name]
    protocol = preset["protocol"]
    is_custom = provider_name.startswith("自定义")

    st.caption(f"协议类型：{'OpenAI 兼容' if protocol == 'openai' else 'Anthropic / Claude 兼容'}")

    input_key = st.text_input("API Key", type="password", placeholder="sk-...")
    st.info("提示：本程序不会存储您的 Key，仅用于当前会话。")

    # base_url：预设只读展示，自定义可编辑
    if is_custom:
        base_url = st.text_input(
            "Base URL",
            value=preset["base_url"],
            placeholder="https://api.example.com/v1",
        )
    else:
        base_url = preset["base_url"]
        st.caption(f"Base URL：`{base_url}`")

    # 模型名：预设给默认值但允许修改，自定义必填
    model_name = st.text_input(
        "模型名称",
        value=preset["model"],
        placeholder="如 deepseek-chat / gpt-4o-mini / deepreasoning-gl-5.2",
    )

    st.divider()
    st.markdown("### 分析参数")
    temp = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    st.write("注：金融分析建议设为 0，保证严谨性。")

# --- 4. 数据加载模块 ---
uploaded_file = st.file_uploader("请上传财务报表 (CSV 或 Excel)", type=["csv", "xlsx"])


@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"文件读取失败: {e}")
        return None


if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:

    # 原始数据预览
        with st.expander("查看原始数据预览"):
            st.dataframe(df.head(10), use_container_width=True)

    # 数据概览
        st.subheader("📊 数据概览")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("数据行数", df.shape[0])

        with col2:
            st.metric("数据列数", df.shape[1])

        with col3:
            st.metric("缺失值数量", int(df.isnull().sum().sum()))

        # 字段信息
        st.subheader("📋 字段信息")

        column_info = pd.DataFrame({
            "字段名称": df.columns,
            "数据类型": df.dtypes.astype(str),
            "缺失值数量": df.isnull().sum().values
        })

        st.dataframe(column_info, use_container_width=True)

        # --- 5. AI 分析模块 ---
        st.subheader("执行智能分析")
        query = st.text_input("💬 请输入您的审计需求或分析指令：", placeholder="例如：分析营收异常值，并画出月度趋势图")

        if st.button("开始分析"):
            if not input_key:
                st.warning("请先在左侧侧边栏输入 API Key！")
            elif not base_url:
                st.warning("请填写 Base URL。")
            elif not model_name:
                st.warning("请填写模型名称。")
            elif not query:
                st.info("请输入具体的需求后再点执行。")
            else:
                with st.spinner("AI 专家正在深度扫描数据并生成报告..."):
                    try:
                        # 根据协议选择客户端：OpenAI 兼容用 ChatOpenAI，
                        # Anthropic/Claude 兼容用 ChatAnthropic（接口格式不同，不可混用）
                        if protocol == "anthropic":
                            from langchain_anthropic import ChatAnthropic
                            llm = ChatAnthropic(
                                model=model_name,
                                temperature=temp,
                                anthropic_api_key=input_key,
                                anthropic_api_url=base_url,
                            )
                        else:
                            llm = ChatOpenAI(
                                model=model_name,
                                temperature=temp,
                                openai_api_key=input_key,
                                base_url=base_url,
                            )

                        # --- 工具调用式 Agent（替代已停维护的 langchain-experimental）---
                        # 用模型原生 tool calling 驱动一个 python_repl 工具，循环执行：
                        # 模型产出 tool_calls → 执行代码 → 把输出/报错回传 → 直到给出最终答案。
                        # 不依赖文本格式解析，OpenAI/Anthropic 协议通用，绘图通过 st.pyplot() 直接渲染。
                        import contextlib
                        import io
                        import traceback
                        import numpy as np
                        import matplotlib
                        from langchain_core.tools import tool as lc_tool
                        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

                        # 持久命名空间：跨多次工具调用保留变量（df、中间结果等）
                        _ns = {"df": df, "pd": pd, "plt": plt, "st": st,
                               "matplotlib": matplotlib, "np": np}

                        @lc_tool
                        def python_repl(code: str) -> str:
                            """执行 Python 代码对 DataFrame df 进行分析与绘图。
                            可用对象：df（数据）、pd、plt、st、matplotlib、np。
                            绘图后必须调用 st.pyplot() 渲染到页面，再用 plt.clf() 清空画布；
                            禁止使用 plt.show() 或 plt.savefig()。"""
                            buf = io.StringIO()
                            try:
                                with contextlib.redirect_stdout(buf):
                                    exec(code, _ns)
                                out = buf.getvalue()
                                return out if out.strip() else "(代码执行完成，无文本输出)"
                            except Exception:
                                return f"代码执行出错：\n{traceback.format_exc()}"

                        tools = [python_repl]
                        llm_with_tools = llm.bind_tools(tools)

                        messages = [
                            SystemMessage(content=(
                                "你是一位资深的金融审计专家。请结合 df 的列名进行逻辑分析，"
                                "确保财务计算准确。需要计算或绘图时调用 python_repl 工具执行代码，"
                                "绘图后用 st.pyplot() 渲染并 plt.clf() 清空画布。"
                                "分析完成后，用中文给出结构化的审计结论。"
                            )),
                            HumanMessage(content=query),
                        ]

                        # 工具调用循环
                        for _ in range(12):
                            resp = llm_with_tools.invoke(messages)
                            messages.append(resp)
                            if not resp.tool_calls:
                                break
                            for tc in resp.tool_calls:
                                fn = {t.name: t for t in tools}.get(tc["name"])
                                result = fn.invoke(tc["args"]) if fn else f"未知工具：{tc['name']}"
                                messages.append(ToolMessage(
                                    content=str(result), tool_call_id=tc["id"]
                                ))

                        final = messages[-1].content if messages[-1].content else "（分析完成，请查看上方图表）"
                        st.chat_message("assistant").markdown(final)

                    except Exception as e:
                        msg = str(e)
                        if "Insufficient Balance" in msg:
                            st.error(f"❌ 余额不足：请检查 {provider_name} 账户余额。")
                        else:
                            st.error(f"❌ 分析中断: {e}")
        # --- 6. 大额交易风险扫描 ---
        st.subheader("🔴 大额交易风险扫描")

        numeric_columns = df.select_dtypes(include="number").columns

        if len(numeric_columns) > 0:
             st.write("检测到的数值字段：", list(numeric_columns))
        else:
             st.warning("当前数据中没有检测到数值字段。")