SMART_STOP_WORDS = {
    # ==========================================================================
    # 组织后缀 (已大幅增强英文部分)
    # ==========================================================================
    "SUFFIXES": [
        # --- 中文部分 (保持不变) ---
        '股份有限公司', '有限责任公司', '股份合作公司', '有限公司', '合伙企业',
        '总公司', '分公司', '公司', '集团', '基金会', '办事处', '合作社',
        '研究所', '设计院', '中心', '协会', '学会', '委员会', '办公室',
        '编辑部', '出版社', '总厂', '分厂', '厂', '部', '店', '行', '社', '所', '院',
        
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
        '信息技术', '网络科技', '数字科技', '科技', '技术', '信息', '网络', '软件', '数据', '智能', '电子', '通信',
        '金融', '银行', '证券', '保险', '投资', '控股', '资产', '资本', '基金', '租赁', '工业', '制造', '实业',
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

import re

def advanced_clean_name(name, stop_word_dict):
    """
    使用分类词库和正则表达式进行更智能的名称清洗。
    """
    # 0. 统一处理英文大小写和前后空格
    clean_name = name.strip().lower()

    # 1. 移除所有标点符号
    punc_pattern = '|'.join(stop_word_dict["PUNCTUATION"])
    clean_name = re.sub(punc_pattern, '', clean_name)

    # 2. 移除字符串末尾的组织后缀
    #    - '|' 用于连接所有后缀，形成一个大的"或"模式
    #    - '$' 表示匹配字符串的结尾
    suffix_pattern = '|'.join(sorted(stop_word_dict["SUFFIXES"], key=len, reverse=True))
    # 按长度排序，优先匹配长的（例如先匹配'股份有限公司'再匹配'公司'）
    clean_name = re.sub(f'({suffix_pattern})$', '', clean_name)

    # 3. 移除字符串开头的地理位置
    #    - '^' 表示匹配字符串的开头
    location_pattern = '|'.join(sorted(stop_word_dict["LOCATIONS"], key=len, reverse=True))
    clean_name = re.sub(f'^({location_pattern})', '', clean_name)
    
    # 4. 移除中间的行业通用词 (这一步要谨慎，可能会误伤)
    #    这里我们仍然使用替换，因为行业词可能出现在任何位置
    for word in sorted(stop_word_dict["INDUSTRIES"], key=len, reverse=True):
        clean_name = clean_name.replace(word, '')

    # 5. 清理多余的空格
    clean_name = clean_name.strip()

    return clean_name


# 数据库记录
db_name = "四川中光防雷科技股份有限公司"
db_aliases_str = "四川中光防雷科技股份有限公司,Sichuan Zhongguang Lightning Protection Technologies Co., Ltd.,中光防雷,四川中光防雷科技有限责任公司"
db_aliases = db_aliases_str.split(',')

# 待匹配的输入
query_name = " 中光防雷科技股份"

# 使用新的智能清洗函数
query_core = advanced_clean_name(query_name, SMART_STOP_WORDS)
db_cores = [advanced_clean_name(alias, SMART_STOP_WORDS) for alias in db_aliases]

print("query_core",query_core)
# 核心匹配逻辑保持不变
is_match = False
for core in db_cores:
    if query_core and query_core == core:  # 确保 query_core 不是空字符串
        print("match",query_core,core)
        is_match = True
        break

print(f"输入: '{query_name}'")
print(f"数据库记录: '{db_name}'")
print("--- 使用智能清洗系统 ---")
print(f"输入的关键词: '{query_core}'")
print(f"数据库别名的关键词: {db_cores}")
print(f"是否匹配: {is_match}")