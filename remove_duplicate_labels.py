import pandas as pd
from thefuzz import fuzz
from itertools import combinations
import os

# --- 步骤 0: 创建演示文件 (如果文件不存在) ---
# 为了让脚本可以独立运行，我们先创建示例文件。
# 如果你已经有了这两个文件，可以注释掉或删除这部分代码。
def create_demo_files():
    # 文件1: only_ranking_without_company.csv
    ranking_data = {
        '榜单名': [
            '2018中国大数据企业50强名单',
            '2022中国AI商业落地TOP100',
            '2023全球独角兽榜'
        ],
        '榜单名简短': [
            '中国大数据企业50强',
            '中国AI商业落地TOP100',
            '全球独角兽榜'
        ]
    }
    pd.DataFrame(ranking_data).to_csv('only_ranking_without_company.csv', index=False, encoding='utf-8-sig')

    # 文件2: 标签名_公司名_带别名_v3.csv
    # 添加一些复杂情况用于测试：
    # - 3M公司: 有一个需要被替换的标签。
    # - 某科技公司: 有两个需要被替换且替换后高度相似的标签，还有一个不相关的。
    # - 另一家公司: 标签替换后完全重复。
    # - 正常公司: 标签各不相同。
    company_data = {
        '标签名': [
            '世界500强',
            '2018中国大数据企业50强名单', # 需要被替换
            '2022中国AI商业落地TOP100',  # 需要被替换
            '中国AI商业落地TOP100',      # 已是简短名
            '2023全球独角兽榜',          # 需要被替换
            '全球独角兽榜',              # 完全重复
            '中国最佳雇主',
            '中国最佳雇主'
        ],
        '公司名': [
            '3M公司',
            '3M公司',
            '某科技公司',
            '某科技公司',
            '另一家公司',
            '另一家公司',
            '正常公司',
            '正常公司' # 故意放一个不同公司的相同标签，以测试分组是否正确
        ],
        '公司别名': [
            '3M公司,3M,3M中国有限公司,3M中国',
            '3M公司,3M,3M中国有限公司,3M中国',
            '某科技,AI Tech',
            '某科技,AI Tech',
            'Unicorn B',
            'Unicorn B',
            'Good Company',
            'Good Company'
        ]
    }
    pd.DataFrame(company_data).to_csv('标签名_公司名_替换后_v4.csv', index=False, encoding='utf-8-sig')

    print("演示文件创建成功！")
    print("-" * 30)

# --- 主要逻辑开始 ---

# 定义文件路径
ranking_file = 'only_ranking_without_company.csv'
company_file = '标签名_公司名_替换后_v5.csv'
output_file = '标签名_公司名_替换后_v6.csv' # 保存替换后结果的文件

# 创建演示文件
if not os.path.exists(ranking_file) or not os.path.exists(company_file):
    # create_demo_files()
    pass

# --- 步骤 1: 读取文件并替换标签名 ---

print("--- 步骤 1: 开始替换标签名 ---")

# 读取两个CSV文件
try:
    mapping_df = pd.read_csv(ranking_file)
    data_df = pd.read_csv(company_file)
except FileNotFoundError as e:
    print(f"错误: 找不到文件 {e.filename}。请确保文件在脚本所在目录。")
    exit()

# 创建一个从“榜单名”到“榜单名简短”的映射字典，这样查找效率更高
# pd.Series(values, index=keys).to_dict() 是一个高效的创建字典的方法
# 创建一个从“榜单名”到“榜单名简短”的映射字典，这样查找效率更高
# pd.Series(values, index=keys).to_dict() 是一个高效的创建字典的方法


# 定义一个自定义函数来处理每个单元格的标签替换
mapping_df.dropna(subset=['榜单名', '榜单名简短'], inplace=True)

# 创建一个从“榜单名”到“榜单名简短”的映射字典
ranking_map = pd.Series(mapping_df['榜单名简短'].values, index=mapping_df['榜单名']).to_dict()

# 定义一个自定义函数来处理每个单元格的标签替换
def replace_tags_in_cell(cell_value, mapping_dict):
    if not isinstance(cell_value, str):
        return cell_value
    original_sub_tags = [tag.strip() for tag in cell_value.split(',')]
    replaced_sub_tags = [mapping_dict.get(tag, tag) for tag in original_sub_tags]
    # 【安全加固】虽然上面已经清理了数据，但这里再加一层保护，确保万无一失
    # 将列表里所有非字符串（以防万一）的元素都转换为字符串
    final_tags = [str(tag) for tag in replaced_sub_tags]
    return ','.join(final_tags)

# 使用 .apply() 方法将上述函数应用到 '标签名' 列的每一个单元格
data_df['标签名'] = data_df['标签名'].apply(replace_tags_in_cell, args=(ranking_map,))

print("标签名替换完成！")
print("替换后数据预览:")
print(data_df.head())
print("标签名替换完成！")
print("替换后数据预览:")
print(data_df.head())


# 将替换后的结果保存到新文件，以便核对
data_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n替换后的完整数据已保存到 '{output_file}'")
print("-" * 30)


# --- 步骤 2: 检查单个公司内，标签名是否重复或高度相似 ---

print("\n--- 步骤 2: 开始检查重复或相似的标签名 ---")

# 设置相似度阈值（例如，85%以上认为是高度相似）
# "中国AI商业落地TOP100" vs "2022中国AI商业落地TOP100" 的 fuzz.ratio 大约为 86
SIMILARITY_THRESHOLD = 60

# 用于存储有问题公司的结果
problematic_companies = {}

# 按“公司名”对数据进行分组
grouped = data_df.groupby('公司名')

for company_name, group in grouped:
    # 获取该公司所有不重复的标签名列表
    tags = group['标签名'].tolist()

    # 如果该公司只有一个标签，则无需比较
    if len(tags) < 2:
        continue

    # 使用itertools.combinations获取所有标签对，避免重复比较 (a,b) 和 (b,a)
    tag_pairs = combinations(tags, 2)

    found_issues = []
    for tag1, tag2 in tag_pairs:
        # 检查是否完全重复 (虽然.unique()已经处理了大部分，但以防万一)
        if tag1 == tag2:
            if (tag1, tag2) not in found_issues and (tag2, tag1) not in found_issues:
                found_issues.append({'type': '完全重复', 'tags': (tag1, tag2), 'score': 100})
            continue # 如果完全重复，就不用再算相似度了

        # 计算两个标签的相似度
        similarity_score = fuzz.ratio(tag1, tag2)

        # 如果相似度高于阈值，则记录下来
        if similarity_score > SIMILARITY_THRESHOLD:
            found_issues.append({'type': '高度相似', 'tags': (tag1, tag2), 'score': similarity_score})

    # 如果为该公司找到了问题，则存入结果字典
    if found_issues:
        problematic_companies[company_name] = found_issues

# --- 步骤 3: 输出检查结果 ---

print("\n--- 检查结果 ---")
if not problematic_companies:
    print("所有公司的标签名均未发现重复或高度相似的情况。")
else:
    print(f"发现 {len(problematic_companies)} 家公司的标签名存在重复或高度相似的情况：\n")
    for company, issues in problematic_companies.items():
        print(f"公司名: 【{company}】")
        for issue in issues:
            print(f"  - 问题类型: {issue['type']}")
            print(f"  - 相似分数: {issue['score']}%")
            print(f"  - 标签 1: '{issue['tags'][0]}'")
            print(f"  - 标签 2: '{issue['tags'][1]}'\n")