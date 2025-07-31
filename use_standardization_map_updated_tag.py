import csv

def build_standardization_map(rules_csv_path):
    """
    根据规则文件构建一个从别名到标准名的映射字典。

    Args:
        rules_csv_path (str): 包含标签标准化规则的CSV文件路径，例如 'tag_clusters_review.csv'。

    Returns:
        dict: 一个映射字典，例如 {'旧标签别名': '标准标签名', '别名2': '标准标签名'}
    """
    tag_map = {}
    print(f"正在从 '{rules_csv_path}' 构建标签标准化规则映射...")
    try:
        with open(rules_csv_path, mode='r', encoding='utf-8-sig') as f:
            # 使用 DictReader 可以方便地通过列名访问数据
            reader = csv.DictReader(f)
            
            for row in reader:
                # 获取标准名（我们决策后的 'last' 列）
                standard_name = row.get('last', '').strip()
                if not standard_name:
                    continue # 如果 'last' 列为空，则跳过此规则

                # 获取所有需要被替换的别名
                # 1. 'Standard_Name_Suggestion' 列本身是一个别名
                suggestion_alias = row.get('Standard_Name_Suggestion', '').strip()
                if suggestion_alias:
                    tag_map[suggestion_alias] = standard_name

                # 2. 'Aliases_Found' 列可能包含多个由 ' | ' 分隔的别名
                aliases_str = row.get('Aliases_Found', '').strip()
                if aliases_str:
                    aliases_list = [alias.strip() for alias in aliases_str.split(' | ')]
                    for alias in aliases_list:
                        if alias:
                            tag_map[alias] = standard_name
        
        print(f"✅ 标签标准化规则映射构建完成，共包含 {len(tag_map)} 条替换规则。")
        return tag_map

    except FileNotFoundError:
        print(f"❌ 严重错误: 规则文件 '{rules_csv_path}' 未找到！请检查文件名和路径。")
        return None
    except Exception as e:
        print(f"❌ 严重错误: 读取规则文件时出错: {e}")
        return None

def standardize_tag_names(data_csv_path, tag_map, output_csv_path):
    """
    遍历数据文件，使用映射字典进行标签名标准化。

    Args:
        data_csv_path (str): 待处理的数据文件路径，例如 '标签名_公司名_final.csv'。
        tag_map (dict): 标签标准化规则的映射字典。
        output_csv_path (str): 最终输出文件的路径。
    """
    print(f"\n正在对 '{data_csv_path}' 中的标签名进行标准化...")
    
    try:
        with open(data_csv_path, 'r', encoding='utf-8-sig') as infile, \
             open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # 读取并写入表头
            header = next(reader)
            writer.writerow(header)
            
            processed_count = 0
            replaced_count = 0

            # 逐行处理数据
            for row in reader:
                if len(row) < 2: continue # 确保行至少有两列
                
                # 读取原始的标签名和公司名
                original_tag_name = row[0].strip()
                company_name = row[1].strip()
                
                # 核心逻辑：在映射字典中查找原始标签名。
                # 如果找到，则返回标准标签名；如果找不到，则返回原始标签名本身。
                standardized_tag_name = tag_map.get(original_tag_name, original_tag_name)
                
                # 检查是否发生了替换，并计数
                if standardized_tag_name != original_tag_name:
                    replaced_count += 1
                
                # 将【标准化后的标签名】和【原始公司名】写入新文件
                writer.writerow([standardized_tag_name, company_name])
                processed_count += 1
            
            print("\n--- 标准化任务总结 ---")
            print(f"总共处理了 {processed_count} 行数据。")
            print(f"成功替换了 {replaced_count} 个标签名为标准名称。")
            print(f"🎉 最终的标准化数据已成功写入到: '{output_csv_path}'")

    except FileNotFoundError:
        print(f"❌ 严重错误: 数据文件 '{data_csv_path}' 未找到！")
    except Exception as e:
        print(f"❌ 严重错误: 处理数据时发生错误: {e}")

if __name__ == '__main__':
    # --- 配置区 ---
    # 输入文件
    # 这是您人工决策后的标签规则文件
    rules_file = 'tag_clusters_review.csv' 
    # 这是待处理的数据文件
    data_file = '标签名_公司名_final.csv'
    
    # 输出文件
    # 这是最终的、干净的数据文件
    final_output_file = '标签名_公司名_final_v1.csv'
    
    # --- 运行主流程 ---
    # 1. 构建标签标准化规则映射
    standardization_rules = build_standardization_map(rules_file)
    
    # 2. 如果规则构建成功，则应用规则进行标签标准化
    if standardization_rules:
        standardize_tag_names(data_file, standardization_rules, final_output_file)