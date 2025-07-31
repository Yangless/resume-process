import pandas as pd
import os

# --- 1. 文件路径定义 ---
# 别名文件
aliases_file = '公司名_别名.csv'
# 标签文件
tags_file = '标签名_公司名_final_v2.csv'
# 输出文件
output_file = '标签名_公司名_带别名_v3.csv'

# --- (可选) 为方便测试，自动生成示例文件 ---
# 如果文件已存在，则跳过此步骤
if not os.path.exists(aliases_file):
    with open(aliases_file, 'w', encoding='utf-8') as f:
        f.write('"公司名","别名"\n')
        f.write('"海尔产业发展有限公司","海尔产城创,海尔产业发展有限公司"\n')
        f.write('"上坤地产集团有限公司","上坤地产集团有限公司,上坤集团,上坤地产"\n')
        f.write('"香港恒泰集团公司","香港恒泰集团公司,恒泰集团,香港恒泰"\n')
        f.write('"腾讯公司","腾讯,Tencent"\n') # 添加一个示例

if not os.path.exists(tags_file):
    with open(tags_file, 'w', encoding='utf-8') as f:
        f.write('标签名,公司名\n')
        f.write('世界500强,3M公司\n')
        f.write('世界500强,ADM公司\n')
        f.write('2024全球保险品牌价值100强排行榜,AFG\n')
        f.write('高科技企业,腾讯公司\n') # 添加一个能匹配上的示例
        f.write('地产企业,上坤地产集团有限公司\n') # 添加另一个能匹配上的示例
        f.write('家电制造,海尔产业发展有限公司\n')

# --- 2. 核心处理逻辑 ---
try:
    print(f"正在读取别名文件: {aliases_file}")
    aliases_df = pd.read_csv(aliases_file)
    
    print(f"正在读取标签文件: {tags_file}")
    tags_df = pd.read_csv(tags_file)

    # 3. 使用左合并 (left merge)
    # 以标签文件(tags_df)为基础，将别名文件(aliases_df)中的信息合并过来
    # on='公司名' 指定了合并的依据是两个文件中都存在的 '公司名' 列
    # how='left' 保证了即使标签文件中的公司在别名文件中找不到，该行也会被保留
    print("正在合并数据...")
    merged_df = pd.merge(tags_df, aliases_df, on='公司名', how='left')

    # 4. 清理数据
    # 合并后，没有找到对应别名的公司，其'别名'列的值会是 NaN (Not a Number)
    # 我们用 .fillna('') 将这些 NaN 值替换为空字符串，使输出更整洁
    # 同时，为了更清晰，可以将新列重命名
    merged_df.rename(columns={'别名': '公司别名'}, inplace=True)
    merged_df['公司别名'] = merged_df['公司别名'].fillna('')

    # 5. 保存结果到新的 CSV 文件
    # index=False: 不将 pandas 的行索引写入文件
    # encoding='utf-8-sig': 确保在 Windows Excel 中打开不会出现中文乱码
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n处理完成！✅")
    print(f"结果已保存到文件: {output_file}")
    print("\n--- 输出文件内容预览 ---")
    print(merged_df)

except FileNotFoundError as e:
    print(f"\n错误：文件未找到，请确认文件 '{e.filename}' 是否存在于脚本相同目录下。")
except Exception as e:
    print(f"\n处理过程中发生错误: {e}")