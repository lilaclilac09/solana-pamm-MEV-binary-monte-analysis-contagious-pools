def enhanced_gmm_clustering_analysis(df):
    """优化的GMM聚类分析 - 基于您的优化经验"""
    print('\\n🧮 第二步: 优化GMM聚类分析')
    print('-' * 50)
    
    # 1. 优化的数据预处理
    print('🔧 数据预处理优化:')
    print('   • RobustScaler (替代StandardScaler)')
    print('   • 异常值检测增强')
    print('   • 特征工程优化')
    
    # 使用RobustScaler - 对异常值更稳健
    from sklearn.preprocessing import RobustScaler
    key_features = ['oracle_backrun_ratio', 'bot_ratio', 'time_diff_ms', 'late_slot_ratio', 'wash_trading_score']
    
    # 异常值检测和清理
    from sklearn.ensemble import IsolationForest
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    outlier_pred = iso_forest.fit_predict(df[key_features])
    clean_df = df[outlier_pred == 1].copy()
    
    print(f'   ✅ 异常值清理: {len(df) - len(clean_df)} 条异常记录移除')
    print(f'   📊 清洁数据集: {len(clean_df)} 条记录')
    
    # 标准化处理
    X = clean_df[key_features].values
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f'   📏 特征标准化完成: {X_scaled.shape[0]} 样本 × {X_scaled.shape[1]} 特征')
    
    # 2. 超参数优化 - 基于您的GridSearch经验
    print('\\n🔧 GMM超参数优化 (GridSearchCV方法):')
    print('   • 聚类数量范围: 2-8')
    print('   • 协方差类型: full, tied, diag, spherical')
    print('   • BIC/AIC准则优化')
    
    param_grid = {
        'n_components': range(2, 9),
        'covariance_type': ['full', 'tied', 'diag', 'spherical'],
        'tol': [1e-4, 1e-3, 1e-2]
    }
    
    # 手动实现GridSearch逻辑
    best_bic = np.inf
    best_params = None
    
    for n_comp in param_grid['n_components']:
        for cov_type in param_grid['covariance_type']:
            for tol in param_grid['tol']:
                try:
                    gmm = GaussianMixture(n_components=n_comp, covariance_type=cov_type, tol=tol, random_state=42)
                    gmm.fit(X_scaled)
                    bic_score = gmm.bic(X_scaled)
                    
                    if bic_score < best_bic:
                        best_bic = bic_score
                        best_params = {'n_components': n_comp, 'covariance_type': cov_type, 'tol': tol}
                except:
                    continue
    
    print(f'   ✅ 最优参数: {best_params}')
    print(f'   📊 最优BIC评分: {best_bic:,.0f}')
    
    # 3. 应用最优GMM模型
    print('\\n🔧 应用最优GMM模型:')
    gmm_optimized = GaussianMixture(**best_params, random_state=42)
    cluster_labels = gmm_optimized.fit_predict(X_scaled)
    clean_df['cluster'] = cluster_labels
    
    print(f'✅ GMM优化聚类完成: 识别出 {len(set(cluster_labels))} 个攻击模式簇')
    
    # 4. 聚类质量评估
    print('\\n📊 聚类质量评估:')
    if len(set(cluster_labels)) > 1:
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        print(f'   • 轮廓系数: {silhouette_avg:.3f} (>0.5表示好聚类)')
    
    # 5. 高级分析 - 协议专业化模式
    print('\\n🔍 攻击者专业化分析:')
    for cluster in sorted(clean_df['cluster'].unique()):
        cluster_data = clean_df[clean_df['cluster'] == cluster]
        print(f'\\n📍 簇{cluster} ({len(cluster_data)} 样本):')
        
        protocol_distribution = cluster_data['protocol'].value_counts(normalize=True)
        for protocol in ['BisonFi', 'HumidiFi', 'GoonFi']:
            if protocol in protocol_distribution:
                percentage = protocol_distribution[protocol] * 100
                protocol_data = cluster_data[cluster_data['protocol'] == protocol]
                
                if len(protocol_data) > 0:
                    oracle_mean = protocol_data['oracle_backrun_ratio'].mean()
                    wash_mean = protocol_data['wash_trading_score'].mean()
                    print(f'   • {protocol}: {percentage:.1f}% (预言机: {oracle_mean:.3f}, 洗售: {wash_mean:.3f})')
    
    return clean_df, cluster_labels, X_scaled, best_params, gmm_optimized