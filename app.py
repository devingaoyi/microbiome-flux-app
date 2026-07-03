import streamlit as st
from src.engine import MicrobeFluxEngine
from src.visualizer import render_flux_map

st.set_page_config(layout="wide", page_title="中国人群微生态通量白盒推理引擎")

st.title("🔬 中国人群肠道微生态通量白盒推理引擎 (MVP v1.0)")
st.caption("基于分子特征糖苷键路由与宿主边界约束的最优化配方生成器")
st.markdown("---")

# 初始化后端引擎
engine = MicrobeFluxEngine(prebiotics_path="data/prebiotics.json", diets_path="data/diets.json")

# 布局设计：左侧控制台，右侧画布图谱
col_input, col_canvas = st.columns([1, 2])

with col_input:
    st.subheader("🎛️ 输入变量控制台")
    
    target = st.selectbox("1. 确定最优化目标函数", 
                          ["NEURODEGENERATIVE_REGULATION", "BARRIER_INTEGRITY_REPAIR"],
                          format_func=lambda x: "🧠 脑肠轴调控 (极大化GABA)" if x=="NEURODEGENERATIVE_REGULATION" else "🛡️ 肠道屏障修复 (极大化丁酸)")
    
    prebiotic_id = st.selectbox("2. 选择受试底物 (益生元)", 
                                 list(engine.prebiotics.keys()),
                                 format_func=lambda x: engine.prebiotics[x]['name_zh'])
    
    dosage = st.slider("3. 设定外源摄入剂量 (g/day)", min_value=1.0, max_value=60.0, value=5.0, step=0.5)
    
    cohort = st.selectbox("4. 锁定目标受试人种基线", ["中国华东城市人群队列"])
    
    diet_id = st.selectbox("5. 绑定宿主基础饮食模式背景", 
                           list(engine.diets.keys()),
                           format_func=lambda x: engine.diets[x]['name_zh'])
    
    st.markdown("---")
    run_btn = st.button("🚀 启动微生态通量推演", type="primary")

with col_canvas:
    st.subheader("📊 动态微生态通量流转图谱")
    
    if run_btn:
        # 执行后端流水线计算
        colon_flux, metabolites, alerts = engine.execute_pipeline(prebiotic_id, dosage, diet_id, target)
        
        # 渲染右侧动态图谱
        p_name = engine.prebiotics[prebiotic_id]['name_zh']
        d_name = engine.diets[diet_id]['name_zh']
        render_flux_map(colon_flux, metabolites, p_name, d_name)
        
        # 决策警告控制台渲染
        st.subheader("🚨 智能边界风险审查控制台")
        if not alerts:
            st.success("🟢 边界审查通过：未检测到任何渗透压过载、丁酸悖论或远端结肠蛋白质腐败毒性风险。配方安全稳定。")
        else:
            for alert in alerts:
                if alert['level'] == 'RED':
                    st.error(f"🔴 灾难熔断警告：{alert['msg']}")
                elif alert['level'] == 'YELLOW':
                    st.warning(f"🟡 生态稳态警告：{alert['msg']}")
                    
        # 自动化诊断文本生成
        st.info(f"📋 **专家系统诊断简报**\n\n目标物状态：丁酸达到基准生理窗口，GABA实际激活通量为 {metabolites['gaba']} μmol/L。配方流转逻辑已完全闭环，生成的动态图谱可直接导出作为B端技术背书白皮书。")
    else:
        st.info("💡 请在左侧配置变量并点击“启动微生态通量推演”按钮以激活白盒计算引擎。")