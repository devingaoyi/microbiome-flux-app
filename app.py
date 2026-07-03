import streamlit as st
from src.engine import MicrobeFluxEngine
from src.visualizer import render_flux_map

st.set_page_config(layout="wide", page_title="中国人群微生态通量白盒推理引擎")

st.title("🔬 中国人群肠道微生态通量白盒推理引擎 (Production v1.0)")
st.caption("基于分子特征糖苷键路由与全品类常规/复杂物料的动态白盒推演系统")
st.markdown("---")

# 初始化泛化后的引擎
engine = MicrobeFluxEngine(
    prebiotics_path="data/prebiotics.json", 
    diets_path="data/diets.json", 
    strains_path="data/strains.json"
)

col_input, col_canvas = st.columns([1, 2])

with col_input:
    st.subheader("🎛️ 全品类变量控制台")
    
    target = st.selectbox(
        "1. 确定最优化目标函数", 
        ["BARRIER_INTEGRITY_REPAIR", "NEURODEGENERATIVE_REGULATION"],
        format_func=lambda x: "🛡️ 肠道屏障修复 (最大化丁酸/尿石素)" if x=="BARRIER_INTEGRITY_REPAIR" else "🧠 脑肠轴调控 (最大化GABA)"
    )
    
    prebiotic_id = st.selectbox(
        "2. 选择受试底物 (全品类开放)", 
        list(engine.prebiotics.keys()),
        format_func=lambda x: engine.prebiotics[x]['name_zh']
    )
    
    dosage = st.slider("3. 设定外源摄入剂量 (g/day)", min_value=1.0, max_value=60.0, value=10.0, step=0.5)
    cohort = st.selectbox("4. 锁定目标受试人种基线", ["中国人群典型肠道宏基因组代表菌库"])
    
    diet_id = st.selectbox(
        "5. 绑定宿主基础饮食模式背景", 
        list(engine.diets.keys()),
        format_func=lambda x: engine.diets[x]['name_zh']
    )
    
    st.markdown("---")
    run_btn = st.button("🚀 启动微生态通量全局推演", type="primary")

with col_canvas:
    st.subheader("📊 动态微生态通量流转图谱")
    
    if run_btn:
        # 执行通用流规则引擎计算
        colon_flux, metabolites, alerts, abundances = engine.execute_pipeline(prebiotic_id, dosage, diet_id, target)
        
        # 渲染动态拓扑图
        p_name = engine.prebiotics[prebiotic_id]['name_zh']
        d_name = engine.diets[diet_id]['name_zh']
        render_flux_map(colon_flux, metabolites, p_name, d_name, abundances)
        
        # 智能边界审查控制台
        st.subheader("🚨 智能边界风险审查控制台")
        if not alerts:
            st.success("🟢 边界审查通过：所有路径未触发渗透压过载、丁酸悖论或远端结肠蛋白质腐败毒性风险。配方生态稳态表现优秀。")
        else:
            for alert in alerts:
                if alert['level'] == 'RED':
                    st.error(f"🔴 灾难熔断警告：{alert['msg']}")
                elif alert['level'] == 'YELLOW':
                    st.warning(f"🟡 生态稳态警告：{alert['msg']}")
                    
        # 智能化动态简报生成
        st.info(f"📋 **配方系统诊断简报**\n\n"
                f"- 结肠净可用碳源通量: {colon_flux:.2f} g/day\n"
                f"- 主要终点代谢物: 丁酸 {metabolites['butyrate']:.1f} mM | GABA {metabolites['gaba']:.1f} μM | 尿石素A {metabolites['urolithin']:.1f} μM\n"
                f"- 潜在毒性副产物(对甲酚): {metabolites['p_cresol']:.1f} mM\n\n"
                f"**白盒推理逻辑：** 系统已成功根据物料分子特征，完成了初级碳源分流与次级交叉喂养网络的级联计算。可直接将本全景通量图谱导出，用于B端产品的科学背书与产品申报说明。")
    else:
        st.info("💡 请在左侧配置变量并点击“启动微生态通量全局推演”按钮以激活白盒计算引擎。")
