from pyvis.network import Network
import streamlit.components.v1 as components

def render_flux_map(colon_flux, metabolites, prebiotic_name, diet_name, abundances):
    net = Network(height="500px", width="100%", bgcolor="#1e1e1e", font_color="#ffffff", directed=True)
    
    gaba_color = "#00e676" if metabolites["gaba"] >= 80.0 else ("#ffb000" if metabolites["gaba"] > 0 else "#757575")
    cresol_color = "#ff5252" if metabolites["p_cresol"] > 2.0 else "#00e676"
    uro_color = "#00e676" if metabolites["urolithin"] > 20.0 else "#757575"
    
    net.add_node("Substrate", label=f"底物: {prebiotic_name}\n(结肠通量: {colon_flux:.2f}g)", color="#97c2fc", shape="ellipse")
    net.add_node("Diet", label=f"饮食背景:\n{diet_name}", color="#ffb000", shape="ellipse")
    
    net.add_node("S_B_inf", label=f"双歧杆菌 (本土)\n丰度: {abundances['S_B_inf_CN01']*100:.1f}%", color="#0288d1", shape="dot", size=int(abundances['S_B_inf_CN01']*100)+10)
    net.add_node("S_B_fra", label=f"脆弱拟杆菌\n丰度: {abundances['S_B_fra_CN03']*100:.1f}%", color="#0288d1", shape="dot", size=int(abundances['S_B_fra_CN03']*100)+10)
    net.add_node("S_F_pra", label=f"普拉梭菌 (丁酸)\n丰度: {abundances['S_F_pra_CN05']*100:.1f}%", color="#26a69a", shape="dot", size=int(abundances['S_F_pra_CN05']*100)+10)
    net.add_node("S_L_bre", label=f"短乳杆菌 (GABA)\n丰度: {abundances['S_L_bre_CN08']*100:.1f}%", color="#b39ddb", shape="dot", size=int(abundances['S_L_bre_CN08']*100)+10)
    net.add_node("S_C_dfi", label=f"艰难梭菌 (毒素株)\n丰度: {abundances['S_C_dfi_CN10']*100:.1f}%", color="#e53935", shape="dot", size=int(abundances['S_C_dfi_CN10']*100)+10)

    net.add_node("Acetate", label=f"乙酸\n{metabolites['acetate']:.1f} mM", color="#00e676", shape="square")
    net.add_node("Propionate", label=f"丙酸\n{metabolites['propionate']:.1f} mM", color="#00e676", shape="square")
    net.add_node("Butyrate", label=f"丁酸 (屏障)\n{metabolites['butyrate']:.1f} mM", color="#00e676", shape="star", size=25)
    net.add_node("GABA", label=f"GABA (脑肠轴)\n{metabolites['gaba']:.1f} μM", color=gaba_color, shape="star", size=25)
    net.add_node("Cresol", label=f"对甲酚 (毒性)\n{metabolites['p_cresol']:.1f} mM", color=cresol_color, shape="diamond")
    net.add_node("Urolithin", label=f"尿石素 A (抗炎)\n{metabolites['urolithin']:.1f} μM", color=uro_color, shape="star", size=25)

    if colon_flux > 0:
        net.add_edge("Substrate", "S_B_inf", value=3, color="#97c2fc")
        net.add_edge("Substrate", "S_B_fra", value=3, color="#97c2fc")
    
    net.add_edge("Diet", "S_L_bre", value=2, color="#ffb000")
    net.add_edge("Diet", "S_C_dfi", value=2, color="#ff5252")
    
    if metabolites["acetate"] > 0:
        net.add_edge("S_B_inf", "Acetate", value=2, color="#00e676")
        net.add_edge("Acetate", "S_F_pra", value=2, color="#26a69a")
    if metabolites["propionate"] > 0:
        net.add_edge("S_B_fra", "Propionate", value=2, color="#00e676")
    if metabolites["butyrate"] > 0:
        net.add_edge("S_F_pra", "Butyrate", value=4, color="#00e676")
    if metabolites["gaba"] > 0:
        net.add_edge("S_L_bre", "GABA", value=4, color=gaba_color)
    if metabolites["p_cresol"] > 2.0:
        net.add_edge("S_C_dfi", "Cresol", value=5, color="#ff5252")
    if metabolites["urolithin"] > 0:
        net.add_edge("Diet", "Urolithin", value=3, color=uro_color)

    net.toggle_physics(True)
    net.save_graph("temp_graph.html")
    with open("temp_graph.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    components.html(html_content, height=520)
