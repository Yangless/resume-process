import json
import csv
from collections import defaultdict

def enrich_tags_from_rankings(json_file_path, csv_file_path, output_csv_path):
    """
    根据JSON榜单文件，扩充或更新CSV中的公司标签。

    Args:
        json_file_path (str): 标准化后的榜单JSON文件路径。
        csv_file_path (str): 原始的“标签名_公司名.csv”文件路径。
        output_csv_path (str): 更新后输出的新CSV文件路径。
    """
    
    # ==============================================================================
    # 步骤 1: 将原始CSV加载到内存中的高效数据结构中
    # 使用 defaultdict(set)，键是公司名，值是该公司的标签集合
    # ==============================================================================
    company_tags_db = defaultdict(set)
    
    print(f"正在从 '{csv_file_path}' 加载原始标签数据...")
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # 尝试读取表头
            try:
                header = next(reader)
                if header != ["标签名", "公司名"]:
                    print(f"⚠️ 警告: CSV文件表头不是预期的 ['标签名', '公司名']，而是 {header}。")
                    # 将第一行也作为数据处理
                    if len(header) == 2:
                        tag, company = header[0].strip(), header[1].strip()
                        if tag and company:
                            company_tags_db[company].add(tag)
            except StopIteration:
                print("ℹ️  信息: CSV文件为空或只有一行。")

            for row in reader:
                if len(row) < 2: continue
                tag, company = row[0].strip(), row[1].strip()
                if tag and company:
                    company_tags_db[company].add(tag)
        print(f"✅ 原始数据加载完成，共 {len(company_tags_db)} 家公司的标签。")
    except FileNotFoundError:
        print(f"ℹ️  信息: 原始标签文件 '{csv_file_path}' 不存在，将创建一个全新的文件。")
    except Exception as e:
        print(f"❌ 严重错误: 读取CSV文件时出错: {e}")
        return

    # ==============================================================================
    # 步骤 2: 加载并遍历JSON榜单文件，更新内存中的数据库
    # ==============================================================================
    print(f"\n正在从 '{json_file_path}' 读取榜单信息进行扩充...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            rankings_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 严重错误: 榜单文件 '{json_file_path}' 未找到！")
        return
    except json.JSONDecodeError:
        print(f"❌ 严重错误: 榜单文件 '{json_file_path}' 不是有效的JSON格式。")
        return
    
    update_count = 0
    new_entry_count = 0
    
    # 遍历每个榜单
    for ranking_name, company_list in rankings_data.items():
        ranking_name = ranking_name.strip()
        if not ranking_name: continue # 跳过空的榜单名
        

        # 遍历榜单下的每个公司
        for company_name in company_list:
            company_name = company_name.strip()
            if not company_name: continue # 跳过空的公司名

            # 1. 记录公司在添加新标签前的存在状态
            # 检查 company_name 是否已经在 company_tags_db 中
            company_existed_before_add = company_name in company_tags_db
            
            # 2. 尝试将榜单名添加到公司的标签集合中
            # 如果 ranking_name 已经存在于该公司的标签集合中，set.add() 不会做任何改变
            # 如果 ranking_name 不存在，set.add() 会添加它
            
            # 为了精确判断是否是“新的标签添加行为”，我们先获取当前标签数量
            initial_tag_count = len(company_tags_db[company_name]) # defaultdict会在此处为新公司创建空集合

            company_tags_db[company_name].add(ranking_name)
            
            # 3. 根据标签数量是否增加来更新计数器
            # 只有当实际添加了新的榜单标签时，才更新计数
            if len(company_tags_db[company_name]) > initial_tag_count:
                if company_existed_before_add:
                    update_count += 1 # 公司已存在，且添加了一个新标签
                else:
                    new_entry_count += 1 # 公司是新添加的，且榜单是它的第一个标签
    
    print("✅ 标签数据扩充完成！")

    # ==============================================================================
    # 步骤 3: 将更新后的内存数据库写回新的CSV文件
    # ==============================================================================
    print(f"\n正在将更新后的数据写入到 '{output_csv_path}'...")
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['标签名', '公司名'])
            
            # 为了输出文件更规整，按公司名排序
            sorted_companies = sorted(company_tags_db.keys())
            
            # 遍历每个公司
            for company in sorted_companies:
                # 获取该公司的所有标签，并排序
                tags = sorted(list(company_tags_db[company]))
                # 将所有标签用逗号连接成一个字符串
                tags_str = ','.join(tags)
                # 写入一行
                writer.writerow([tags_str, company])
                
        print("\n--- 任务总结 ---")
        print(f"更新了 {update_count} 家已有公司的标签。")
        print(f"新增了 {new_entry_count} 家公司的条目。")
        print(f"最终数据库包含 {len(company_tags_db)} 家公司的标签信息。")
        print(f"🎉  所有数据已成功写入到: '{output_csv_path}'")

    except Exception as e:
        print(f"🔥  严重错误: 无法将数据写入到 '{output_csv_path}': {e}")


if __name__ == '__main__':
    # --- 配置区 ---
    # 输入文件
    json_rankings_file = 'normalized_rankings.json'
    csv_tags_file = '标签名_公司名.csv'
    
    # 输出文件 (使用新名字以避免覆盖原始文件)
    output_csv_file = '标签名_公司名_updated.csv'
    
    # --- 运行主函数 ---
    enrich_tags_from_rankings(json_rankings_file, csv_tags_file, output_csv_file)