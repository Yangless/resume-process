import os
import json
import csv
import re
from collections import defaultdict

# ==============================================================================
# 步骤 1: 定义清洗函数和停用词库 
# ==============================================================================

SMART_STOP_WORDS = {
    # ==========================================================================
    # 组织后缀 (已大幅增强英文部分)
    # ==========================================================================
    "SUFFIXES": [
        # --- 中文部分 (保持不变) ---
        '股份有限公司', '有限责任公司', '股份合作公司', '有限公司', '合伙企业',
        '总公司', '分公司', '公司', '集团', '基金会', '办事处', '合作社',
        '研究所', '设计院', '中心', '协会', '学会', '委员会', '办公室',
        '编辑部', '出版社', '总厂', '分厂',
        
        # --- 英文常见形式 (按长度降序排列) ---
        'corporation', 'incorporated', 'co.,ltd.', 'co., ltd.', 'co.,ltd',
        'company', 'limited', 'co.ltd', 'co ltd', 'group', 'corp.', 'corp',
        'inc.', 'inc', 'llc', 'ltd.', 'ltd', 'co.', 'co',
        # --- 其他国际形式 ---
        'gmbh', 's.a.', 's.l.', 'a.g.', 'pty ltd'
    ],

    # ==========================================================================
    # 地理位置 (保持不变)
    # ==========================================================================
     "LOCATIONS": [
        # ============================ 中文部分 (保留) ============================
        # --- 直辖市 ---
        '北京市', '北京', '天津市', '天津', '上海市', '上海', '重庆市', '重庆',
        # --- 华北地区 ---
        '河北省', '河北', '石家庄市', '石家庄', '唐山市', '唐山',
        '山西省', '山西', '太原市', '太原', '大同市', '大同',
        '内蒙古自治区', '内蒙古', '呼和浩特市', '呼和浩特', '包头市', '包头',
        # --- 东北地区 ---
        '辽宁省', '辽宁', '沈阳市', '沈阳', '大连市', '大连',
        '吉林省', '吉林', '长春市', '长春',
        '黑龙江省', '黑龙江', '哈尔滨市', '哈尔滨', '大庆市', '大庆',
        # --- 华东地区 ---
        '江苏省', '江苏', '南京市', '南京', '苏州市', '苏州', '无锡市', '无锡',
        '浙江省', '浙江', '杭州市', '杭州', '宁波市', '宁波', '温州市', '温州',
        '安徽省', '安徽', '合肥市', '合肥', '福建省',
        '福建', '福州市', '福州', '厦门市', '厦门', '泉州市', '泉州',
        '江西省', '江西', '南昌市', '南昌',
        '山东省', '山东', '济南市', '济南', '青岛市', '青岛', '烟台市', '烟台',
        # --- 华中地区 ---
        '河南省', '河南', '郑州市', '郑州', '洛阳市', '洛阳',
        '湖北省', '湖北', '武汉市', '武汉', '宜昌市', '宜昌',
        '湖南省', '湖南', '长沙市', '长沙',
        # --- 华南地区 ---
        '广东省', '广东', '广州市', '广州', '深圳市', '深圳', '东莞市', '东莞', '佛山市', '佛山', '珠海市', '珠海',
        '广西壮族自治区', '广西', '南宁市', '南宁', '桂林市', '桂林',
        '海南省', '海南', '海口市', '海口', '三亚市', '三亚',
        # --- 西南地区 ---
        '四川省', '四川', '成都市', '成都', '绵阳市', '绵阳',
        '贵州省', '贵州', '贵阳市', '贵阳',
        '云南省', '云南', '昆明市', '昆明',
        '西藏自治区', '西藏', '拉萨市', '拉萨',
        # --- 西北地区 ---
        '陕西省', '陕西', '西安市', '西安',
        '甘肃省', '甘肃', '兰州市', '兰州',
        '青海省', '青海', '西宁市', '西宁',
        '宁夏回族自治区', '宁夏', '银川市', '银川',
        '新疆维吾尔自治区', '新疆', '乌鲁木齐市', '乌鲁木齐',
        # --- 港澳台 ---
        '香港', '澳门', '台湾',
        # --- 通用地理后缀 ---
        '省', '市', '县', '区', '自治州', '地区', '镇', '乡', '村',

        # ============================ 英文/拼音部分 (新增) ============================
        # --- 国家 ---
        'china', 'p.r.c', 'prc',
        # --- 直辖市 ---
        'beijing shi', 'beijing', 'tianjin shi', 'tianjin', 'shanghai shi', 'shanghai', 'chongqing shi', 'chongqing',
        # --- 华北 ---
        'hebei province', 'hebei sheng', 'hebei', 'shijiazhuang', 'tangshan',
        'shanxi province', 'shanxi sheng', 'shanxi', 'taiyuan', 'datong',
        'inner mongolia autonomous region', 'inner mongolia', 'neimenggu', 'hohhot', 'baotou',
        # --- 东北 ---
        'liaoning province', 'liaoning sheng', 'liaoning', 'shenyang', 'dalian',
        'jilin province', 'jilin sheng', 'jilin', 'changchun',
        'heilongjiang province', 'heilongjiang sheng', 'heilongjiang', 'harbin', 'daqing',
        # --- 华东 ---
        'jiangsu province', 'jiangsu sheng', 'jiangsu', 'nanjing', 'suzhou', 'wuxi',
        'zhejiang province', 'zhejiang sheng', 'zhejiang', 'hangzhou', 'ningbo', 'wenzhou',
        'anhui province', 'anhui sheng', 'anhui', 'hefei',
        'fujian province', 'fujian sheng', 'fujian', 'fuzhou', 'xiamen', 'quanzhou',
        'jiangxi province', 'jiangxi sheng', 'jiangxi', 'nanchang',
        'shandong province', 'shandong sheng', 'shandong', 'jinan', 'qingdao', 'tsingtao', 'yantai',
        # --- 华中 ---
        'henan province', 'henan sheng', 'henan', 'zhengzhou', 'luoyang',
        'hubei province', 'hubei sheng', 'hubei', 'wuhan', 'yichang',
        'hunan province', 'hunan sheng', 'hunan', 'changsha',
        # --- 华南 ---
        'guangdong province', 'guangdong sheng', 'guangdong', 'kwangtung',
        'guangzhou shi', 'guangzhou', 'canton',
        'shenzhen shi', 'shenzhen', 'dongguan', 'foshan', 'zhuhai',
        'guangxi zhuang autonomous region', 'guangxi', 'nanning', 'guilin',
        'hainan province', 'hainan sheng', 'hainan', 'haikou', 'sanya',
        # --- 西南 ---
        'sichuan province', 'sichuan sheng', 'sichuan', 'szechuan', 'chengdu', 'mianyang',
        'guizhou province', 'guizhou sheng', 'guizhou', 'guiyang',
        'yunnan province', 'yunnan sheng', 'yunnan', 'kunming',
        'tibet autonomous region', 'tibet', 'xizang', 'lhasa',
        # --- 西北 ---
        'shaanxi province', 'shaanxi sheng', 'shaanxi', 'xi\'an', 'xian',
        'gansu province', 'gansu sheng', 'gansu', 'lanzhou',
        'qinghai province', 'qinghai sheng', 'qinghai', 'xining',
        'ningxia hui autonomous region', 'ningxia', 'yinchuan',
        'xinjiang uyghur autonomous region', 'xinjiang', 'urumqi',
        # --- 港澳台 ---
        'hong kong', 'hongkong', 'hk', 'macau', 'macao', 'taiwan',
        # --- 英文通用地理后缀 ---
        'province', 'city', 'county', 'district', 'town', 'village', 'autonomous region', 'prefecture', 'region'
    ],

    # ==========================================================================
    # 行业/通用词 (已增强英文部分)
    # ==========================================================================
    "INDUSTRIES": [
        # --- 中文部分 ---
        '信息技术', '网络科技', '在线','数字科技', '科技', '技术', '信息', '网络', '软件', '数据', '智能', '电子', '通信',
        '金融',  '控股', '资产', '资本', '基金', '租赁', '工业', '制造', '实业',
        '工程', '装备', '能源', '化工', '材料', '生物', '医药', '贸易', '进出口', '商贸', '物流', '供应链',
        '建筑', '建设', '房产', '地产', '置业', '物业', '文化', '传媒', '广告', '咨询', '服务', '发展', '管理',
        
        # --- 英文部分 ---
        'technology', 'science', 'engineering', 'information', 'electronics', 'energy', 'biology',
        'investment', 'finance', 'holdings', 'trading', 'international', 'tech', 'sci', 'info'
    ],
    
    # ==========================================================================
    # 标点/连接符 (保持不变)
    # ==========================================================================
    "PUNCTUATION": [
        r'\(', r'\)', r'（', r'）', r'\[', r'\]', r'【', r'】',
        r'·', r'&', r',', r'/', r'\.', r'、'
    ]
}

def advanced_clean_name(name, stop_word_dict):
    """沿用match_and_add_tags"""
    if not isinstance(name, str): return ""
    clean_name = name.strip().lower()
    punc_pattern = '|'.join(stop_word_dict["PUNCTUATION"])
    clean_name = re.sub(punc_pattern, ' ', clean_name)
    suffix_pattern = '|'.join(sorted(stop_word_dict["SUFFIXES"], key=len, reverse=True))
    clean_name = re.sub(r'(\s*\b(' + suffix_pattern + r')\b\s*)+$', '', clean_name)
    location_pattern = '|'.join(sorted(stop_word_dict["LOCATIONS"], key=len, reverse=True))
    clean_name = re.sub(f'^({location_pattern})', '', clean_name)
    industry_pattern = r'\b(' + '|'.join(sorted(stop_word_dict["INDUSTRIES"], key=len, reverse=True)) + r')\b'
    clean_name = re.sub(industry_pattern, '', clean_name)
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    return clean_name

import re

def advanced_clean_name_v1(name, stop_word_dict):
    """
    1. 优先删除'-'及其后面的所有内容。
    2. 接着删除括号及其内部的所有内容。
    """
    if not isinstance(name, str): return ""
    
    clean_name = name.strip()
    # print("strip",clean_name)
    # ==================== 核心改进点 V3 ====================
    # 步骤 0.1: 优先移除'-'及其后面的所有内容
    # 使用 split 获取第一个连字符之前的部分，并去除可能存在的空格
    clean_name = clean_name.split('-', 1)[0].strip()
    # print("存在的空格",clean_name)
    # 步骤 0.2: 接着移除所有括号（中英文）及其内部的内容
    clean_name = re.sub(r'[（\(][^）)]*[）\)]', '', clean_name)
    # ======================================================
    # print("括号",clean_name)
    """
    使用分类词库和正则表达式进行更智能的名称清洗。
    """
    # 0. 统一处理英文大小写和前后空格
    clean_name = clean_name.strip().lower()
    # print("英文大小",clean_name)
    # 1. 移除所有标点符号
    punc_pattern = '|'.join(stop_word_dict["PUNCTUATION"])
    clean_name = re.sub(punc_pattern, '', clean_name)
    # print("移除所有标点符号",clean_name)
    # 2. 移除字符串末尾的组织后缀
    #    - '|' 用于连接所有后缀，形成一个大的"或"模式
    #    - '$' 表示匹配字符串的结尾
    # 步骤 3: 移除字符串末尾的组织后缀
    suffix_pattern = '|'.join(sorted(stop_word_dict["SUFFIXES"], key=len, reverse=True))
    clean_name = re.sub(r'(\s*(' + suffix_pattern + r')\s*)', '', clean_name)
    # print("SUFFIXES",clean_name)
    # 步骤 4: 移除字符串开头的地理位置
    # location_pattern = '|'.join(sorted(stop_word_dict["LOCATIONS"], key=len, reverse=True))
    # clean_name = re.sub(f'({location_pattern})', '', clean_name)
    # print("LOCATIONS",clean_name)
    # 步骤 5: 移除中间的行业/通用词
    # industry_pattern =  '|'.join(sorted(stop_word_dict["INDUSTRIES"], key=len, reverse=True)) 
    # clean_name = re.sub(industry_pattern, '', clean_name)
    # print("INDUSTRIES",clean_name)


    # suffix_pattern = '|'.join(sorted(stop_word_dict["SUFFIXES"], key=len, reverse=True))
    # # 按长度排序，优先匹配长的（例如先匹配'股份有限公司'再匹配'公司'）
    # clean_name = re.sub(f'({suffix_pattern})$', '', clean_name)
    # # print("SUFFIXES",clean_name)
    # # 3. 移除字符串开头的地理位置
    # #    - '^' 表示匹配字符串的开头
    # location_pattern = '|'.join(sorted(stop_word_dict["LOCATIONS"], key=len, reverse=True))
    # clean_name = re.sub(f'^({location_pattern})', '', clean_name)
    # # print("LOCATIONS",clean_name)
    # # 4. 移除中间的行业通用词 (这一步要谨慎，可能会误伤)
    # #    这里我们仍然使用替换，因为行业词可能出现在任何位置
    # for word in sorted(stop_word_dict["INDUSTRIES"], key=len, reverse=True):
    #     clean_name = clean_name.replace(word, '')
    # print("INDUSTRIES",clean_name)
    # 5. 清理多余的空格
    clean_name = clean_name.strip()
    # print("空格",clean_name)
    return clean_name

# advanced_clean_name_v1("腾讯科技（深圳）深圳集团股份有限公司", SMART_STOP_WORDS)
# exit(0)
# ==============================================================================
# 步骤 2: 构建高效的内存查找数据库
# ==============================================================================
def build_lookup_database(csv_file_path):
    """
    从CSV文件构建一个 '核心关键词 -> 标准公司名' 的查找字典。
    这是整个流程中性能优化的关键。
    """
    lookup_dict = {}
    print(f"正在从 '{csv_file_path}' 构建查找数据库...")
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as f: # 'utf-8-sig'能处理带BOM的文件
            reader = csv.reader(f)
            # 跳过表头
            header = next(reader)
            if header != ["公司名", "别名"]:
                print(f"⚠️ 警告: CSV文件表头不是预期的 ['公司名', '别名']，而是 {header}。将继续处理。")

            for row in reader:
                if len(row) < 2: continue # 跳过不完整的行
                
                standard_name = row[0].strip()
                aliases_str = row[1].strip()
                
                # 获取所有待处理的名称（标准名 + 所有别名）
                all_names = [standard_name] + [alias.strip() for alias in aliases_str.split(',') if alias.strip()]
                
                for name in all_names:
                    # 清洗每一个名称，得到核心关键词
                    core_keyword = advanced_clean_name_v1(name, SMART_STOP_WORDS)
                    
                    # 如果核心关键词非空，且尚未在字典中（避免低优先级别名覆盖高优先级）
                    if core_keyword and core_keyword not in lookup_dict:
                        lookup_dict[core_keyword] = standard_name
                        
    except FileNotFoundError:
        print(f"❌ 严重错误: 数据库文件 '{csv_file_path}' 未找到！请检查文件名和路径。")
        return None
    except Exception as e:
        print(f"❌ 严重错误: 读取CSV文件时出错: {e}")
        return None
    
    print(f"✅ 查找数据库构建完成，包含 {len(lookup_dict)} 个唯一的关键词。")
    return lookup_dict

# ==============================================================================
# 步骤 3: 主逻辑 - 遍历、匹配、替换
# ==============================================================================
def standardize_rankings(input_json_path, db_lookup, output_json_path):
    """
    遍历榜单JSON，使用查找字典进行名称标准化。
    """
    print(f"\n正在处理榜单文件: '{input_json_path}'")
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            original_rankings = json.load(f)
    except FileNotFoundError:
        print(f"❌ 严重错误: 榜单文件 '{input_json_path}' 未找到！")
        return
    except json.JSONDecodeError:
        print(f"❌ 严重错误: 榜单文件 '{input_json_path}' 不是有效的JSON格式。")
        return

    normalized_rankings = {}
    success_count = 0
    failure_count = 0

    # 遍历每个榜单
    for ranking_name, company_list in original_rankings.items():
        new_company_list = []
        # 遍历榜单下的每个公司
        for company_name in company_list:
            # 清洗榜单中的公司名，得到查询关键词
            query_core = advanced_clean_name_v1(company_name, SMART_STOP_WORDS)
            
            is_match = False
            # 进行高效的字典查找，而不是循环比较
            if query_core and query_core in db_lookup:
                standard_name = db_lookup[query_core]
                new_company_list.append(standard_name)
                success_count += 1
                is_match = True
            
            if not is_match:
                # 如果匹配失败，保留原名并输出提示
                new_company_list.append(company_name)
                print(f"  - 匹配失败: [榜单: {ranking_name}] - 公司: {company_name} - 清洗：{query_core}")
                failure_count += 1
        
        # 将处理后的公司列表存入新的字典
        # 使用 set 去重，保留原始顺序相对困难，这里直接去重并排序
        normalized_rankings[ranking_name] = sorted(list(set(new_company_list)))

    print("\n标准化处理完成！")
    
    # 保存结果到新的JSON文件
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_rankings, f, ensure_ascii=False, indent=2)

        print("\n--- 任务总结 ---")
        print(f"✔️  成功匹配并标准化的记录数: {success_count}")
        print(f"❌  匹配失败的记录数: {failure_count}")
        print(f"🎉  标准化后的数据已成功写入到: '{output_json_path}'")
        
    except Exception as e:
        print(f"🔥  严重错误: 无法将结果写入到 '{output_json_path}': {e}")


if __name__ == '__main__':
    # --- 配置区 ---
    # 输入文件
    aggregated_json_file = 'aggregated_rankings.json'
    database_csv_file = './res/公司名_别名.csv'
    
    # 输出文件
    normalized_json_file = 'normalized_rankings.json'
    
    # --- 运行主流程 ---
    # 1. 构建内存数据库
    lookup_db = build_lookup_database(database_csv_file)
    
    # 2. 如果数据库构建成功，则执行标准化
    if lookup_db:
        standardize_rankings(aggregated_json_file, lookup_db, normalized_json_file)