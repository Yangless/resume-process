import os
import re
import jieba
import json

import pandas as pd
import requests
from rapidfuzz import process, fuzz

company_url=os.getenv('COMPANY_URL','http://172.16.1.38:8887/Elasticsearch/knowledgeGraphQuery?dataName=enterprise&queryName=')
class IndustryMatcher:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            try:
                file_path = os.path.join(current_dir, 'company_new.json')
                file_path1 = os.path.join(current_dir, 'company_map.json')
            except Exception as e:
                print(e)
                file_path = os.path.join('/app/res', 'company_new.json')
                file_path1 = os.path.join('/app/res', 'company_map.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                self.df_dict = json.loads(f.read())
            with open(file_path1, 'r', encoding='utf-8') as f:
                self.df_dict_map = json.loads(f.read())
            self.df_dict_map_f={value:key for key,value in self.df_dict_map.items()}

            file_path3 = os.path.join(current_dir, '行业带别名.csv')
            self.df = pd.read_csv(file_path3)
        except Exception as e:
            raise RuntimeError("加载company_new.json失败") from e

        self._initialized = True

    @staticmethod
    def _cut(word):
        word = word.replace('/', '')
        return ' '.join(jieba.lcut(word, cut_all=False)).lower()

    async def industry_nor(self, industry_name):
        result = []
        industry = []
        flag = True
        try:
            position_name_list = industry_name.replace(' ', '').replace('(', '').replace(')', '').split('/')
            for position_name_i in position_name_list:
                if '-' in position_name_i:
                    position_name_i=re.findall(r'(.*)-',position_name_i)[0]
                cleaned = position_name_i
                match, score, _ = process.extractOne(
                    cleaned,
                    list(self.df_dict.keys()),
                    scorer=fuzz.ratio
                )
                match1, score1, _ = process.extractOne(
                    cleaned,
                    list(self.df_dict_map.values()),
                    scorer=fuzz.ratio
                )

                if score > 90:
                    flag = False
                    standard_name=match
                    result.append(standard_name)
                    company_map=self.df_dict_map.get(standard_name,'')
                    if company_map:
                        result.append(company_map)
                    industry.extend(self.df_dict[match])
                elif score1>90:
                    flag = False
                    standard_name = match1
                    result.append(standard_name)
                    industry.extend(self.df_dict[self.df_dict_map_f[standard_name]])
                else:
                    pattern=re.compile(r'(.*?)(?:公司|集团)')
                    position_name_i_re=pattern.search(position_name_i)
                    if position_name_i_re:
                        result.append(position_name_i_re.group())
        except Exception as e:
            print(e)
        #print(industry)

        if flag:
            try:
                response = requests.get(
                    f'{company_url}{industry_name}',
                    timeout=2
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'company' in data and 'name' in data['company']:
                        result.append(data['company']['name'])
                    if 'industries' in data and isinstance(data['industries'], list):
                        industry.extend([i['name'] for i in data['industries']])
            except Exception as e:
                print("远程请求失败:", e)
        if industry:
            industry=[i.replace('行业','').replace('相关','') for i in industry]
            return {"公司": list(set(result)), "行业": [re.sub(r'业$','',i) for i in industry]}
        else:return {"公司": list(set(result)), "行业": industry}

    async def industry_nor1(self, industry_name):
        industry = []
        position_name_list = industry_name.replace(' ', '').replace('(', '').replace(')', '').split('/')
        position_name_list = [i.replace('行业', '').replace('相关', '') for i in position_name_list]
        position_name_list1 = [re.sub(r'业$', '', i) for i in position_name_list]
        position_name_list.extend(position_name_list1)
        position_name_list = list(set(position_name_list))

        for position_name_i in position_name_list:
            try:
                mask = self.df['别名'].str.split(',').apply(lambda x: position_name_i in x)
                df_1 = self.df[mask]
                industry.extend(list(df_1.iloc[:,0]))
                """
                response = requests.get(
                    f'http://172.16.1.38:8887/Elasticsearch/knowledgeGraphQuery?dataName=industry&queryName={position_name_i}',
                    timeout=2
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'cluster' in data and isinstance(data['cluster'], list):
                        for item in data['cluster']:
                            if 'name' in item:
                                industry.append(item['name'])
                else:industry.append(industry_name)
                """
            except Exception as e:
                if position_name_i.lower() in ['saas','软件即服务']:
                    industry.append('saas')
                print(f"请求失败 ({position_name_i}):", e)
        if industry:
            industry=[i.replace('行业','').replace('相关','') for i in industry]
            # [re.sub(r'业$','',i) for i in industry if len(i)>2]
            return industry
        else:
            return industry
    async def process_industry1(self,key,value):
        desired_industry = await self.industry_nor1(value)
        return {'INDUSTRY':desired_industry}



#matcher = IndustryMatcher()
#a=["上海聚均科技有限公司","上海证大资产管理有限公司","新沃基金管理有限公司","新沃资本控股集团有限公司"]
#['金康幼儿园', '分众传媒', '中国移动通信股份有限公司福州分公司', '分众传媒信息技术股份有限公司']
#print(matcher.industry_nor('欧莱雅中国'))
#print(matcher.industry_nor1("通信"))