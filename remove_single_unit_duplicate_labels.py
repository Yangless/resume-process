import pandas as pd
from thefuzz import fuzz
from itertools import combinations
import os

# --- 主要逻辑开始 ---

# 定义文件路径
ranking_file = 'only_ranking_without_company.csv'
company_file = '标签名_公司名_替换后_v6.csv'
output_file = '标签名_公司名_替换后_v7.csv'

# 创建演示文件
if not os.path.exists(ranking_file) or not os.path.exists(company_file):
    # create_demo_files()
    pass

# --- 步骤 1: 读取文件并替换标签名 ---

print("--- 步骤 1: 开始替换标签名 ---")

try:
    mapping_df = pd.read_csv(ranking_file)
    data_df = pd.read_csv(company_file)
except FileNotFoundError as e:
    print(f"错误: 找不到文件 {e.filename}。请确保文件在脚本所在目录。")
    exit()

ranking_map = pd.Series(mapping_df['榜单名简短'].values, index=mapping_df['榜单名']).to_dict()
data_df['标签名'] = data_df['标签名'].replace(ranking_map)

print("标签名替换完成！")
data_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"替换后的完整数据已保存到 '{output_file}'")
print("-" * 30)

# --- 步骤 2: 检查单个公司内，不同行的标签名是否重复或高度相似 ---

print("\n--- 步骤 2: 检查【公司间】标签相似性 (一个公司的多个标签行) ---")

# 设置相似度阈值
SIMILARITY_THRESHOLD = 90
problematic_companies_inter = {} # 用于存储公司间问题的结果

grouped = data_df.groupby('公司名')

for company_name, group in grouped:
    tags = group['标签名'].unique().tolist()
    if len(tags) < 2:
        continue

    tag_pairs = combinations(tags, 2)
    found_issues = []
    for tag1, tag2 in tag_pairs:
        # 确保标签是字符串类型再进行比较
        if not isinstance(tag1, str) or not isinstance(tag2, str):
            continue
            
        similarity_score = fuzz.ratio(tag1, tag2)
        if similarity_score > SIMILARITY_THRESHOLD:
            # 检查是否完全一样
            issue_type = '完全重复' if similarity_score == 100 else '高度相似'
            found_issues.append({'type': issue_type, 'tags': (tag1, tag2), 'score': similarity_score})

    if found_issues:
        problematic_companies_inter[company_name] = found_issues



# --- 步骤 3: 检查并修正单个标签单元格内部的相似子标签 (修正版) ---

print("\n--- 步骤 3: 修正单元格内相似的子标签 (保留短的) ---")

# 设置相似度阈值
SIMILARITY_THRESHOLD = 85
modification_logs = []

for index, row in data_df.iterrows():
    tag_cell = row['标签名']
    
    if not isinstance(tag_cell, str) or ',' not in tag_cell:
        continue

    # 原始子标签列表
    sub_tags = [t.strip() for t in tag_cell.split(',')]
    
    if len(sub_tags) < 2:
        continue

    # 创建一个列表的副本，我们将从这个副本中移除元素
    # 我们保留 sub_tags 作为原始参考
    final_tags = list(sub_tags)
    
    # 记录已经处理过的对，防止重复处理
    processed_pairs = set()

    # 使用索引来遍历，避免迭代器问题
    for i in range(len(sub_tags)):
        for j in range(i + 1, len(sub_tags)):
            tag1 = sub_tags[i]
            tag2 = sub_tags[j]
            
            # 创建一个唯一的键来代表这个组合 (排序后)，以检查是否已处理
            pair_key = tuple(sorted((tag1, tag2)))
            if pair_key in processed_pairs:
                continue
            
            similarity_score = fuzz.ratio(tag1, tag2)
            
            if similarity_score > SIMILARITY_THRESHOLD:
                # 确定要移除的标签
                tag_to_remove = None
                if len(tag1) > len(tag2):
                    tag_to_remove = tag1
                elif len(tag2) > len(tag1):
                    tag_to_remove = tag2
                else: # 长度相等，包括完全相同的情况
                    tag_to_remove = tag1 # 任意移除一个，这里选择移除第一个

                # 只有当要移除的标签还在 final_tags 列表中时，才执行移除
                # .remove() 方法只会移除第一个匹配到的元素
                if tag_to_remove in final_tags:
                    final_tags.remove(tag_to_remove)
                    processed_pairs.add(pair_key) # 标记这对已经处理过了

    # 检查内容是否真的发生了变化
    new_tag_cell = ','.join(final_tags)
    if new_tag_cell != tag_cell:
        data_df.at[index, '标签名'] = new_tag_cell
        modification_logs.append({
            'company': row['公司名'],
            'index': index,
            'original_cell': tag_cell,
            'new_cell': new_tag_cell
        })

# --- 打印修改日志 ---
if modification_logs:
    print(f"\n完成了 {len(modification_logs)} 处单元格内部标签的修正。详情如下:")
    for log in modification_logs:
        print(f"  - 公司: {log['company']} (行索引: {log['index']})")
        print(f"    原始值: '{log['original_cell']}'")
        print(f"    修正后: '{log['new_cell']}'\n")
else:
    print("\n未发现单元格内需要修正的相似子标签。")



# --- 步骤 4: 将最终处理结果保存到新的CSV文件 ---

final_output_file = '标签名_公司名_替换后_v8.csv'

print("\n" + "="*40)
print(f"所有处理步骤完成，正在将最终结果保存到文件: {final_output_file}")

try:
    # index=False: 不将DataFrame的索引写入到CSV文件中。
    # encoding='utf-8-sig': 确保Excel能正确显示中文。
    data_df.to_csv(final_output_file, index=False, encoding='utf-8-sig')
    print(f"文件保存成功！")
except Exception as e:
    print(f"错误：文件保存失败！原因: {e}")

print("="*40)