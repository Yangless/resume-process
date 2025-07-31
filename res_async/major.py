import os

import pandas as pd
from rapidfuzz import process,fuzz
class MajorMatcher:
    _instance=None
    _initialized=False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance=super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._initialized:
            return
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, '知识图谱专业带别名.csv')
            df = pd.read_csv(file_path)
            self.df_set = set(df['专业名'].unique())
        except Exception as e:
            raise RuntimeError("加载知识图谱专业带别名失败") from e
        self._initialized = True

    async def major_nor(self,major_name):
        major_name=major_name.replace(' ','').replace(',','')
        major_list=major_name.split('/')
        result = []
        for i in major_list:
            match, score, _ = process.extractOne(i, list(self.df_set), scorer=fuzz.token_set_ratio)
            if score > 85:
                #print(f'{match},{score}')
                result.append(match)
            else:
                result.append(i)
        return list(set(result))
    async def process_major(self,key,value):
        major_list=[]
        major = await self.major_nor(value)
        if major:
            major_list.extend(major)
        else:
            major_list.append(value)
        return {key:major_list}

#match=MajorMatcher()
#print(match.major_nor('机械电子工程/机电一体化'))