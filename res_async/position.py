import os
import re
import jieba
import pandas as pd
import json
from rapidfuzz import process, fuzz


class PositionNormalizer:
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
            current_dir1 = os.path.dirname(os.path.abspath(__file__))
            file_path1 = os.path.join(current_dir1, 'position.json')
            with open(file_path1, 'r', encoding='utf-8') as f:
                df_dict = json.loads(f.read())
        except Exception as e:
            raise RuntimeError("加载position.json 失败") from e

        self.df_dict_f = {j: key for key, value in df_dict.items() for j in value}

        try:
            current_dir2 = os.path.dirname(os.path.abspath(__file__))
            file_path2 = os.path.join(current_dir2, '知识图谱职位带别名.csv')
            self.df = pd.read_csv(file_path2)

        except Exception as e:
            raise RuntimeError("加载知识图谱职位带别名.csv 失败") from e
        self._initialized=True

        def cut(word):
            word = word.replace('/', '')
            word = ' '.join(jieba.lcut(word, cut_all=False))
            return word.lower()

        self._cut = cut
        self.standard_position = {
            self._cut(i): i for i in self.df_dict_f.keys()
        }
        self.position_csv = {self._cut(i): i for i in self.df['职位名']}
        self._initialized = True

    async def position_nor(self, position_name):
        try:
            #position_name=re.sub(r'[ ,、|；:]+', '', position_name.strip())
            position_name = re.sub(r'[|,，、/]+', ' ', position_name.strip()[:30])
            position_name = re.sub(r'\s+', ' ', position_name)
            position_name=position_name.lower()
            result = []
            industry = []
            other=[]

            position_name_list_=position_name.strip().split(' ')
            #position_name_list_.append(position_name.strip())
            position_name_list=position_name_list_
            """
            position_name_list = position_name_list_
            if len(position_name_list)<2:
                position_name_list = position_name.strip().split(',')
                if len(position_name_list) < 2:
                    position_name_list = position_name.strip().split('/')
            """
            #position_name_list=[position_name]
            for position_name_i in position_name_list:
                cleaned = self._cut(position_name_i)

                match1,score1,_ = process.extractOne(
                    cleaned,
                    list(self.position_csv.keys()),
                    scorer=fuzz.token_set_ratio,
                )
                if score1>88:
                    result.append(self.position_csv[match1])
                    industry.append(self.df[self.df['职位名']==self.position_csv[match1]].iloc[0,0])
                """
                matches = process.extract(
                    cleaned,
                    list(self.standard_position.keys()),
                    scorer=fuzz.token_set_ratio,
                    limit=6
                )
                for match,score,_ in matches:
                    print(match,score)
                    if score > 88:
                        matched_position = self.standard_position.get(match, '')
                        if matched_position:
                            result.append(matched_position)
                            industry.append(self.df_dict_f[matched_position])
                        elif ('创业' not in position_name_i) or (':' not in position_name_i) or ('：' not in position_name_i):
                            result.append(position_name_i)
                """
                mask = self.df['别名'].str.lower().str.split(',').apply(lambda x: position_name_i in x)
                df_1 = self.df[mask]
                result.extend(list(df_1.iloc[:,2]))
                if len(list(df_1.iloc[:,2]))>0 or score1>88:
                    other.append(position_name_i)
                industry.extend(list(df_1.iloc[:,0]))
            result_else = set(position_name_list)-set(other) - set([i.lower() for i in result])
            if not os.path.exists('./data/'):
                os.makedirs('./data/')
            if result_else:
                with open ('./data/position.txt','a',encoding='utf-8') as f:
                    f.writelines([i+'\n' for i in result_else])
            return {"职位": list(set(result)), "行业": list(set(industry))}
        except Exception as e:
            print('position出错',e)
    async def process_position(self,key,value):
        position_dict = await self.position_nor(value)
        return [{'POSITION':position_dict['职位']},{'INDUSTRY':position_dict['行业']}]
#matcher = PositionNormalizer()
#a="物流主管 物流专员/助理 仓库经理/主管 客服主管 采购员  "
#a=["城市客户经理","区域客户经理","市场客户经理","销售客户经理"]
#a=["后端开发","后端工程师","服务端开发","Golang工程师","Python工程师"]
#print(matcher.position_nor('产品设计师'))