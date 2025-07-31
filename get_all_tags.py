import json
import csv

# --- 1. 定义文件路径 ---
json_file_path = 'aggregated_rankings.json'
csv_file_path = 'only_ranking_without_company.csv'

# --- (可选) 为方便测试，自动生成示例 JSON 文件 ---
# 如果文件已存在，则跳过此步骤
import os
if not os.path.exists(json_file_path):
    json_data = {
      "2018中国大数据企业50强名单": [
        "华为",
        "四方伟业",
        "浪潮",
        "滴滴",
        "联想",
        "腾讯",
        "阿里巴巴"
      ],
      "2018年（第17届）中国软件业务收入前百家企业": [
        "万达信息股份有限公司",
        "上海华东电脑股份有限公司",
        "上海华讯网络系统有限公司"
      ],
      "2023福布斯中国最具创新力企业TOP50": [
        "比亚迪",
        "宁德时代",
        "小米"
      ]
    }
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


# --- 2. 核心处理逻辑 ---
try:
    # 读取 JSON 文件
    print(f"正在读取 JSON 文件: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取所有的键 (keys)
    rank_names = list(data.keys())
    print("成功提取以下榜单名:")
    for name in rank_names:
        print(f"- {name}")

    # 写入 CSV 文件
    print(f"\n正在写入 CSV 文件: {csv_file_path}")
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as f:
        # 创建一个 writer 对象
        writer = csv.writer(f)

        # 写入表头
        writer.writerow(['榜单名', '榜单别名'])

        # 逐行写入榜单名
        for name in rank_names:
            # 写入一行数据，第二列'榜单别名'留空
            writer.writerow([name, ''])

    print("\n处理完成！✅")
    print(f"结果已保存到文件: {csv_file_path}")

except FileNotFoundError:
    print(f"\n错误：文件 '{json_file_path}' 未找到，请确认文件名和路径是否正确。")
except json.JSONDecodeError:
    print(f"\n错误：文件 '{json_file_path}' 不是一个有效的 JSON 格式文件。")
except Exception as e:
    print(f"\n处理过程中发生未知错误: {e}")