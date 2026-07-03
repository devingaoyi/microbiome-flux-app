import json

class MicrobeFluxEngine:
    def __init__(self, prebiotics_path, diets_path, strains_path):
        with open(prebiotics_path, 'r', encoding='utf-8') as f:
            self.prebiotics = {item['prebiotic_id']: item for item in json.load(f)}
        with open(diets_path, 'r', encoding='utf-8') as f:
            self.diets = {item['diet_id']: item for item in json.load(f)}
        with open(strains_path, 'r', encoding='utf-8') as f:
            self.strains = json.load(f)

    def execute_pipeline(self, prebiotic_id, dosage, diet_id, target_objective):
        p_meta = self.prebiotics[prebiotic_id]
        d_meta = self.diets[diet_id]
        
        # 1. 小肠吸收衰减计算
        colon_flux = dosage * (1.0 - p_meta['host_loss_rate'])
        
        # 2. 初始化效应物积累池
        metabolites = {"acetate": 0.0, "propionate": 0.0, "butyrate": 0.0, "lactate": 0.0, "gaba": 0.0, "p_cresol": 0.0, "urolithin": 0.0}
        precursors = {"fucose": 0.0, "glutamate": d_meta['baseline_glutamate'], "tyrosine": d_meta['baseline_tyrosine'], "polyphenol": d_meta['baseline_polyphenol']}
        alerts = []
        
        # 3. 动态配置丰度基线
        if d_meta['diet_id'] == "Diet_High_Fiber_001":
            abundances = {"S_B_inf_CN01": 0.05, "S_B_bif_CN02": 0.02, "S_B_fra_CN03": 0.05, "S_P_cop_CN04": 0.40, "S_F_pra_CN05": 0.20, "S_A_muc_CN06": 0.03, "S_E_hal_CN07": 0.05, "S_L_bre_CN08": 0.10, "S_R_gna_CN09": 0.02, "S_C_dfi_CN10": 0.01}
        elif d_meta['diet_id'] == "Diet_Western_Urban_002":
            abundances = {"S_B_inf_CN01": 0.01, "S_B_bif_CN02": 0.01, "S_B_fra_CN03": 0.35, "S_P_cop_CN04": 0.02, "S_F_pra_CN05": 0.05, "S_A_muc_CN06": 0.08, "S_E_hal_CN07": 0.02, "S_L_bre_CN08": 0.02, "S_R_gna_CN09": 0.25, "S_C_dfi_CN10": 0.05}
        else: 
            abundances = {"S_B_inf_CN01": 0.15, "S_B_bif_CN02": 0.08, "S_B_fra_CN03": 0.15, "S_P_cop_CN04": 0.10, "S_F_pra_CN05": 0.15, "S_A_muc_CN06": 0.10, "S_E_hal_CN07": 0.05, "S_L_bre_CN08": 0.15, "S_R_gna_CN09": 0.03, "S_C_dfi_CN10": 0.01}

        # 4. 目标函数特异性增益因子（模拟最优化选择）
        # 如果用户选择了特定健康目标，系统模拟临床推荐，对特定降解菌的代谢活性赋予非线性增益权重
        if target_objective == "GLUCOSE_METABOLISM_MANAGEMENT":
            abundances["S_B_fra_CN03"] *= 1.5  # 模拟控糖目标下，富集能高效产生丙酸的脆弱拟杆菌
        elif target_objective == "IMMUNE_HOMEOSTASIS":
            abundances["S_P_cop_CN04"] *= 1.3  # 模拟免疫调控下，传统高纤普雷沃氏菌的响应权重

        # 5. 轨道A/B：初级碳源降解动态分流检索
        active_degraders = []
        total_affinity = 0.0
        
        if p_meta['substrate_class'] == "Sugar_Alcohol":
            active_degraders.append(("S_B_fra_CN03", abundances["S_B_fra_CN03"] * 2.0))
            total_affinity = abundances["S_B_fra_CN03"] * 2.0
            abundances["S_B_inf_CN01"] *= 0.5
        elif p_meta['substrate_class'] == "Polyphenol":
            precursors["polyphenol"] += colon_flux * 5.0
            colon_flux = 0.0 
        else:
            for strain in self.strains:
                if strain['eco_role'] == "Primary_Degrader":
                    match_count = 0
                    for linkage in p_meta['glycosidic_linkages']:
                        if "Fuc" in linkage and ("GH29" in strain['cazymes'] or "GH95" in strain['cazymes']): match_count += 1
                        if "Fructan" in linkage and "GH32" in strain['cazymes']: match_count += 1
                        if "Glc" in linkage and "GH13" in strain['cazymes']: match_count += 1
                    
                    if match_count > 0:
                        affinity = match_count * abundances[strain['strain_id']]
                        active_degraders.append((strain['strain_id'], affinity))
                        total_affinity += affinity

        primary_acetate = 0.0
        primary_lactate = 0.0
        
        if total_affinity > 0 and colon_flux > 0:
            for strain_id, affinity in active_degraders:
                allocated_share = affinity / total_affinity
                strain_flux = colon_flux * allocated_share
                
                if "inf" in strain_id or "bif" in strain_id:
                    primary_acetate += strain_flux * 2.5
                    primary_lactate += strain_flux * 1.5
                else: 
                    primary_acetate += strain_flux * 1.8
                    metabolites["propionate"] += strain_flux * 1.5 # 激活高通量丙酸流
                
                strain_meta = next(s for s in self.strains if s['strain_id'] == strain_id)
                if strain_meta.get('location') == "Extracellular" and "2FL" in prebiotic_id:
                    precursors["fucose"] += strain_flux * 0.4  

        # 6. 轨道C：次级交叉喂养与前体偶联动态推演
        total_butyrate_producers_abundance = abundances["S_F_pra_CN05"] + abundances["S_E_hal_CN07"]
        if total_butyrate_producers_abundance > 0 and (primary_acetate > 0 or primary_lactate > 0):
            metabolites["butyrate"] += (primary_lactate * 0.8 + primary_acetate * 0.4) * (total_butyrate_producers_abundance / 0.25)
            metabolites["acetate"] = primary_acetate * 0.6
            metabolites["lactate"] = primary_lactate * 0.2
        else:
            metabolites["acetate"] = primary_acetate
            metabolites["lactate"] = primary_lactate

        if abundances["S_L_bre_CN08"] > 0 and precursors["fucose"] > 0 and precursors["glutamate"] > 5.0:
            metabolites["gaba"] = min(precursors["glutamate"] * 5.0, 80.0) * (abundances["S_L_bre_CN08"] / 0.15) * 1.5
        
        if prebiotic_id == "P_PPH_ELL_011" or precursors["polyphenol"] > 10.0:
            if abundances["S_C_dfi_CN10"] < 0.04: 
                metabolites["urolithin"] = precursors["polyphenol"] * 4.2 * (abundances["S_B_inf_CN01"] / 0.15 + 0.5)

        # 7. 远端结肠蛋白质厌氧发酵毒性检查与边界熔断
        if colon_flux < 2.5 and d_meta['diet_id'] == "Diet_Western_Urban_002":
            metabolites["p_cresol"] = precursors["tyrosine"] * 0.32 * (abundances["S_C_dfi_CN10"] / 0.05)
            alerts.append({"level": "RED", "msg": "远端结肠碳源完全断裂！艰难梭菌触发蛋白质腐败发酵，对甲酚毒性严重超标。"})

        if dosage > p_meta['osmotic_laxative_threshold']:
            alerts.append({"level": "YELLOW", "msg": f"单次摄入剂量突破该原料耐受上限({p_meta['osmotic_laxative_threshold']}g)，触发高风险渗透性宿主腹泻与严重肠胀气警告。"})
        
        if metabolites["butyrate"] > 30.0:
            alerts.append({"level": "YELLOW", "msg": "警告：局部丁酸浓度超过 30 mmol/L 上限，触发“丁酸悖论”，存在破坏隐窝干细胞及诱导正常结肠细胞凋亡的风险。"})
            metabolites["butyrate"] = 30.0 - (metabolites["butyrate"] - 30.0) * 0.5 

        return colon_flux, metabolites, alerts, abundances
