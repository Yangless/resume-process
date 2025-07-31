import pandas as pd
import re
from thefuzz import fuzz
from collections import defaultdict

# ==============================================================================
# 步骤 1: 专为“标签”设计的清洗预处理函数
# ==============================================================================
def robust_clean_tag_name(tag):
    """
    一个专用于标签聚类预处理的清洗函数。
    它会移除榜单、年份、地理位置等通用噪音词。
    """
    if not isinstance(tag, str): return ""
    
    # 移除连字符和括号及其内容
    clean_tag = tag.split('-', 1)[0].strip()
    clean_tag = re.sub(r'[（\(][^）)]*[）\)]', '', clean_tag)
    
    # 转为小写
    clean_tag = clean_tag.lower()

    # 定义需要移除的噪音词 (针对榜单/标签名)
    stop_words = [
        '中国', '企业', '公司', '集团', '控股', '股份', '上市',
        '榜单', '名单', '排名', '强', '家', '榜',
        '年度', '发布', '最新', '年',
        'the', 'of', 'and', 'in' # 简单的英文停用词
    ]
    
    # 移除所有数字 (通常是年份或排名数字，会干扰相似度判断)
    clean_tag = re.sub(r'\d+', '', clean_tag)

    # 使用单词边界\b进行精确移除
    for word in stop_words:
        clean_tag = re.sub(r'\b' + re.escape(word) + r'\b', '', clean_tag)
        
    # 清理多余空格
    clean_tag = re.sub(r'\s+', ' ', clean_tag).strip()
    
    return clean_tag

# ==============================================================================
# 步骤 2: 聚类函数 (保持通用性)
# ==============================================================================
def cluster_items(items, preprocess_func, threshold=85):
    """
    通用的聚类函数，接收一个预处理函数。

    Args:
        items (list): 待聚类的字符串列表 (这里是标签名)。
        preprocess_func (function): 用于预处理每个字符串的函数。
        threshold (int): 相似度阈值。

    Returns:
        list: 聚类结果，每个元素是一个包含相似项的集合(set)。
    """
    print(f"开始对 {len(items)} 个唯一项进行聚类，阈值={threshold}%...")
    clusters = []
    
    preprocessed_map = {item: preprocess_func(item) for item in items}
    
    sorted_items = sorted(items, key=lambda x: len(preprocessed_map[x]), reverse=True)

    for item in sorted_items:
        processed_item = preprocessed_map[item]
        if not processed_item: continue

        found_cluster = False
        for cluster in clusters:
            representative = next(iter(cluster))
            processed_representative = preprocessed_map[representative]
            
            score = fuzz.token_set_ratio(processed_item, processed_representative)
            
            if score > threshold:
                cluster.add(item)
                found_cluster = True
                break
        
        if not found_cluster:
            clusters.append({item})
            
    print(f"聚类完成，共形成 {len(clusters)} 个簇。")
    return clusters

# ==============================================================================
# 步骤 3: 主执行流程 (已修改为处理标签)
# ==============================================================================
def main():
    """
    主执行函数
    """
    input_csv = '标签名_公司名_final.csv'
    output_csv = 'tag_clusters_for_review.csv'
    
    # --- 1. 加载并提取所有唯一的标签名 ---
    try:
        df = pd.read_csv(input_csv, encoding='utf-8-sig', usecols=['标签名'])
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_csv}' 不存在。")
        return
    except ValueError:
        print(f"错误：输入文件 '{input_csv}' 中未找到'标签名'列。")
        return

    # 将"标签名"列中的逗号分隔字符串拆分成列表
    df['标签名'] = df['标签名'].astype(str).str.split(',')
    # 使用 explode 将列表中的每个元素扩展成新行
    exploded_df = df.explode('标签名')
    # 清理前后空格并删除空行
    exploded_df['标签名'] = exploded_df['标签名'].str.strip()
    exploded_df.dropna(subset=['标签名'], inplace=True)
    exploded_df = exploded_df[exploded_df['标签名'] != '']
    
    # 获取所有唯一的标签名
    unique_tags = exploded_df['标签名'].unique().tolist()
    
    # --- 2. 对唯一标签进行聚类 ---
    # 对于标签，阈值可以适当放宽，例如85
    tag_clusters = cluster_items(unique_tags, 
                                 preprocess_func=robust_clean_tag_name, 
                                 threshold=70)
    
    # --- 3. 准备并输出供人工审核的结果 ---
    review_data = []
    for i, cluster in enumerate(tag_clusters):
        # 只要簇里有内容就输出，因为即使是单个标签也可能需要标准化
        if cluster:
            # 选择簇中最长的名字作为建议的标准名
            suggested_standard_name = max(cluster, key=len)
            
            # 其他名字作为别名
            aliases = sorted(list(cluster - {suggested_standard_name}))
            
            review_data.append({
                'Cluster_ID': i + 1,
                'Standard_Name_Suggestion': suggested_standard_name,
                'Aliases_Found': ' | '.join(aliases),
                'Cluster_Size': len(cluster)
            })
        
    review_df = pd.DataFrame(review_data)
    # 按簇的大小降序排列，优先审核最可能重复的组
    review_df = review_df.sort_values(by='Cluster_Size', ascending=False)
    
    review_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"\n🎉 任务完成！共发现 {len(review_df)} 个标签簇。")
    print(f"请打开 '{output_csv}' 文件进行人工审核。")

if __name__ == '__main__':
    main()