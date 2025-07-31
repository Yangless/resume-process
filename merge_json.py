import os
import json
from collections import defaultdict

def aggregate_by_ranking(root_folders, output_file):
    """
    遍历指定的根文件夹，按榜单名称聚合所有 company_list.json 文件。
    最终生成一个以榜单名为键，公司列表为值的字典。
    """
    # 使用 defaultdict(list) 可以极大地简化代码
    # 当访问一个不存在的键时，它会自动创建一个空列表作为默认值
    aggregated_data = defaultdict(list)
    
    processed_files_count = 0
    skipped_empty_count = 0
    skipped_missing_count = 0

    print("开始按榜单聚合任务...")
    print(f"扫描文件夹: {', '.join(root_folders)}")
    print("-" * 30)

    # 1. 遍历每一个主文件夹
    for folder in root_folders:
        if not os.path.isdir(folder):
            print(f"⚠️  警告: 文件夹 '{folder}' 不存在，已跳过。")
            continue

        print(f"\n正在处理主文件夹: '{folder}'")
        
        # 2. 遍历主文件夹下的所有榜单子文件夹
        for subfolder_name in os.listdir(folder):
            subfolder_path = os.path.join(folder, subfolder_name)

            if os.path.isdir(subfolder_path):
                json_path = os.path.join(subfolder_path, 'company_list.json')

                # 3. 检查 company_list.json 是否存在
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # ==================== 核心逻辑修改处 ====================
                        
                        found_data_in_file = False
                        
                        # 只处理字典格式: {"榜单名": [...]}
                        if isinstance(data, dict) and data:
                            for ranking_name, company_list in data.items():
                                # 确保榜单名不为空，且公司列表是有效的列表
                                if ranking_name and isinstance(company_list, list) and company_list:
                                    # 使用 defaultdict 的魔力！
                                    # 如果 ranking_name 不存在，会自动创建 aggregated_data[ranking_name] = []
                                    # 然后 extend 操作
                                    aggregated_data[ranking_name].extend(company_list)
                                    
                                    print(f"  ✅ 已聚合: {json_path} (榜单'{ranking_name}', {len(company_list)}条记录)")
                                    found_data_in_file = True
                        
                        # ======================================================
                        
                        if found_data_in_file:
                            processed_files_count += 1
                        else:
                            skipped_empty_count += 1
                            print(f"  🟡 已跳过 (空内容或非字典格式): {json_path}")

                    except json.JSONDecodeError:
                        print(f"  ❌ 错误: 文件 '{json_path}' 不是有效的JSON格式，已跳过。")
                    except Exception as e:
                        print(f"  ❌ 错误: 读取文件 '{json_path}' 时发生未知错误: {e}")
                else:
                    skipped_missing_count += 1
    
    print("-" * 30)
    print("\n聚合任务完成！")

    # 为了更好的可读性，对最终结果的键（榜单名）进行排序
    sorted_aggregated_data = dict(sorted(aggregated_data.items()))
    
    # 可选：对每个榜单下的公司列表去重并排序
    for ranking_name in sorted_aggregated_data:
        # 使用 set 去重，然后转回 list 并排序
        unique_companies = sorted(list(set(sorted_aggregated_data[ranking_name])))
        sorted_aggregated_data[ranking_name] = unique_companies

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_aggregated_data, f, ensure_ascii=False, indent=2)
        
        print("\n--- 任务总结 ---")
        print(f"✔️  成功处理文件数量: {processed_files_count}")
        print(f"✔️  聚合后总榜单数: {len(sorted_aggregated_data)}")
        total_companies = sum(len(v) for v in sorted_aggregated_data.values())
        print(f"✔️  所有榜单下公司总数 (去重后): {total_companies}")
        print(f"🟡  因内容为空/格式不符而跳过的文件数: {skipped_empty_count}")
        print(f"🎉  所有数据已成功写入到: '{output_file}'")

    except Exception as e:
        print(f"🔥  严重错误: 无法将数据写入到 '{output_file}': {e}")


if __name__ == '__main__':
    # --- 配置区 ---
    folders_to_scan = [
        'web_rankings_pdf_output',
        'web_rankings_pdf_output2',
        'web_rankings_pdf_output3'
    ]
    # 修改输出文件名以反映新的数据结构
    final_output_file = 'aggregated_rankings.json'

    # --- 运行主函数 ---
    aggregate_by_ranking(folders_to_scan, final_output_file)