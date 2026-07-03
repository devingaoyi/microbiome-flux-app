from pyvis.network import Network
import streamlit.components.v1 as components

def render_flux_map(colon_flux, metabolites, prebiotic_name, diet_name):
    # 初始化 Pyvis 交互网络，采用黑白暗色背景增强科学质感
    net = Network(height="500px", width="100%", bgcolor="#1e1e1e", font_color="#ffffff", directed=True)
    
    # 添加四层节点
    net.add_node("Substrate", label=f"底物: {prebiotic_name}\n(结肠净通量: {colon_flux:.2f}g)", color="#97c2fc", shape="ellipse")
    net.add_node("Diet", label=f"饮食背景:\n{diet_name}", color="#ffb000", shape="ellipse")
    
    net.add_node("B_bifidum", label="两栖双歧杆菌\n(初级降解菌)", color="#4caf50", shape="dot", size=25)
    net.add_node("L_brevis", label="短乳杆菌\n(次级转化菌)", color="#4caf50", shape="dot", size=20)
    
    net.add_node("Pool_Fucose", label="游离岩藻糖池\n(中间体)", color="#e91e63", shape="box")
    
    # 依据计算输出动态改变效应物节点的颜色（红绿灯机制）
    gaba_color = "#00e676" if metabolites["gaba"] >= 100.0 else "#ff5252"
    cresol_color = "#ff5252" if metabolites["p_cresol"] > 2.0 else "#00e676"
    
    net.add_node("Butyrate", label=f"丁酸 (屏障靶点)\n{metabolites['butyrate']:.1f} mmol/L", color="#00e676", shape="star", size=30)
    net.add_node("GABA", label=f"GABA (脑肠轴)\n{metabolites['gaba']:.1f} μmol/L", color=gaba_color, shape="star", size=30)
    net.add_node("Cresol", label=f"对甲酚 (毒性指标)\n{metabolites['p_cresol']:.1f} mmol/L", color=cresol_color, shape="diamond", size=25)

    # 拓扑连线与通量粗细计算
    net.add_edge("Substrate", "B_bifidum", value=3.5, title="主要降解流", color="#97c2fc")
    net.add_edge("B_bifidum", "Pool_Fucose", value=2.0, title="胞外剪切释放", color="#e91e63")
    net.add_edge("Pool_Fucose", "L_brevis", value=1.5, color="#ffffff")
    net.add_edge("Diet", "L_brevis", value=2.0, title="游离谷氨酸驱动", color="#ffb000")
    
    net.add_edge("B_bifidum", "Butyrate", value=float(metabolites['butyrate'])*0.2, color="#00e676")
    net.add_edge("L_brevis", "GABA", value=float(metabolites['gaba'])*0.02, color=gaba_color)
    
    if metabolites["p_cresol"] > 0.0:
        net.add_edge("Diet", "Cresol", value=float(metabolites['p_cresol'])*0.5, title="蛋白质厌氧腐败通量", color="#ff5252")

    # 启用物理引擎实现平滑动效
    net.toggle_physics(True)
    
    # 编译并存为临时 HTML
    net.save_graph("temp_graph.html")
    
    # 读出并渲染进 Streamlit
    with open("temp_graph.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    components.html(html_content, height=520)