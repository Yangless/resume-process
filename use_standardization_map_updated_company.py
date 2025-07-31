import csv

def build_standardization_map(rules_csv_path):
    """
    Args:
        rules_csv_path (str): 'company_clusters_review.csv' 的路径。

    Returns:
        dict: 一个映射字典，例如 {'海尔集团公司': '海尔集团公司', '别名2': '标准名'}
    """
    name_map = {}
    print(f"正在从 '{rules_csv_path}' 构建标准化规则映射...")
    try:
        with open(rules_csv_path, mode='r', encoding='utf-8-sig') as f:
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
                    name_map[suggestion_alias] = standard_name

                # 2. 'Aliases_Found' 列可能包含多个由 ' | ' 分隔的别名
                aliases_str = row.get('Aliases_Found', '').strip()
                if aliases_str:
                    aliases_list = [alias.strip() for alias in aliases_str.split(' | ')]
                    for alias in aliases_list:
                        if alias:
                            name_map[alias] = standard_name
        
        print(f"✅ 标准化规则映射构建完成，共包含 {len(name_map)} 条替换规则。")
        return name_map

    except FileNotFoundError:
        print(f"❌ 严重错误: 规则文件 '{rules_csv_path}' 未找到！请检查文件名和路径。")
        return None
    except Exception as e:
        print(f"❌ 严重错误: 读取规则文件时出错: {e}")
        return None

def standardize_company_names(data_csv_path, name_map, output_csv_path):
    """
    遍历数据文件，使用映射字典进行公司名标准化。

    Args:
        data_csv_path (str): '标签名_公司名_updated.csv' 的路径。
        name_map (dict): 标准化规则的映射字典。
        output_csv_path (str): 最终输出文件的路径。
    """
    print(f"\n正在对 '{data_csv_path}' 中的公司名进行标准化...")
    
    # 使用with语句同时打开读写文件
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
                if len(row) < 2: continue
                
                tags, original_company_name = row[0], row[1].strip()
                
                # 核心逻辑：使用 .get() 方法进行查找和替换
                # 如果在map中找到，则返回标准名；如果找不到，则返回原始名称本身。
                standardized_name = name_map.get(original_company_name, original_company_name)
                
                # 检查是否发生了替换，并计数
                if standardized_name != original_company_name:
                    replaced_count += 1
                
                # 写入新的一行
                writer.writerow([tags, standardized_name])
                processed_count += 1
            
            print("\n--- 标准化任务总结 ---")
            print(f"总共处理了 {processed_count} 行数据。")
            print(f"成功替换了 {replaced_count} 个公司名为标准名称。")
            print(f"🎉  最终的标准化数据已成功写入到: '{output_csv_path}'")

    except FileNotFoundError:
        print(f"❌ 严重错误: 数据文件 '{data_csv_path}' 未找到！")
    except Exception as e:
        print(f"❌ 严重错误: 处理数据时发生错误: {e}")

if __name__ == '__main__':
    # --- 配置区 ---
    # 输入文件
    # 这是您人工决策后的规则文件
    rules_file = 'tag_clusters_review.csv' 
    # 这是待处理的数据文件
    data_file = '标签名_公司名_final.csv'
    
    # 输出文件
    # 这是最终的、干净的数据文件
    final_output_file = '标签名_公司名_final_v2.csv'
    
    # --- 运行主流程 ---
    # 1. 构建规则映射
    standardization_rules = build_standardization_map(rules_file)
    
    # 2. 如果规则构建成功，则应用规则
    if standardization_rules:
        standardize_company_names(data_file, standardization_rules, final_output_file)