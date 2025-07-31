import csv
import collections

def merge_tags_for_companies(input_csv_path, output_csv_path):
    """
    读取CSV文件，将相同公司的标签合并，并去除重复标签。

    Args:
        input_csv_path (str): 输入的CSV文件路径 ('标签名_公司名_final_v1.csv')。
        output_csv_path (str): 输出的CSV文件路径。
    """
    # 使用字典来存储每个公司的标签集合。
    # key: 公司名 (str)
    # value: 标签集合 (set)
    # collections.defaultdict(set) 能简化代码，当访问一个不存在的key时，会自动创建一个空集合。
    company_tags_map = collections.defaultdict(set)

    print(f"正在从 '{input_csv_path}' 读取数据...")
    try:
        with open(input_csv_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.reader(infile)
            
            # 跳过表头
            header = next(reader)
            
            processed_rows = 0
            # 遍历每一行，构建 company_tags_map
            for row in reader:
                if len(row) < 2:
                    continue # 跳过格式不正确的行
                
                tag_name = row[0].strip()
                company_name = row[1].strip()
                
                if not company_name:
                    continue # 跳过公司名为空的行
                
                # 将标签添加到对应公司的集合中，集合会自动处理重复项
                company_tags_map[company_name].add(tag_name)
                processed_rows += 1

        print(f"数据读取完成。共处理 {processed_rows} 行，发现 {len(company_tags_map)} 个独立公司。")

    except FileNotFoundError:
        print(f"❌ 严重错误: 输入文件 '{input_csv_path}' 未找到！")
        return
    except Exception as e:
        print(f"❌ 严重错误: 读取文件时出错: {e}")
        return

    print(f"\n正在将合并后的数据写入到 '{output_csv_path}'...")
    try:
        with open(output_csv_path, mode='w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.writer(outfile)
            
            # 写入新的表头
            writer.writerow(['标签名', '公司名'])
            
            # 遍历聚合后的字典
            for company_name, tags_set in company_tags_map.items():
                # 为了输出结果稳定，可以对标签进行排序
                sorted_tags = sorted(list(tags_set))
                
                # 使用逗号将所有标签合并成一个字符串
                # csv.writer 会自动处理需要加引号的情况（当字符串中包含逗号时）
                merged_tags = ",".join(sorted_tags)
                
                # 写入新的一行
                writer.writerow([merged_tags, company_name])
                
        print("\n--- 合并任务总结 ---")
        print(f"🎉 成功将 {len(company_tags_map)} 个公司的标签合并并写入到 '{output_csv_path}'")

    except Exception as e:
        print(f"❌ 严重错误: 写入文件时出错: {e}")


if __name__ == '__main__':
    # --- 配置区 ---
    # 输入文件 (包含重复公司的文件)
    input_file = '标签名_公司名_final_v1.csv'
    
    # 输出文件 (标签合并后的最终文件)
    output_file = '标签名_公司名_final_v2.csv'
    
    # --- 运行主流程 ---
    merge_tags_for_companies(input_file, output_file)