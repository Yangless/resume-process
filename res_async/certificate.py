import os
import re
import jieba
import pandas as pd
from rapidfuzz import process, fuzz


class CertificateNormalizer:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CertificateNormalizer, cls).__new__(cls)
            cls._instance.load_data()
            print('加载')
        return cls._instance

    def cut(self,word):
        word = word.replace('(', '').replace(')', '').replace('（', '').replace('）', '')
        word = ' '.join(jieba.lcut(word, cut_all=False))
        return word.lower()

    def load_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, '知识图谱证书带别名1.csv')
        self.df = pd.read_csv(file_path)
        df_set = set(self.df['证书名'])
        self.df['别名']=list(map(lambda x:x.lower(),self.df['别名']))
        self.standard_skills = {self.cut(i): i for i in df_set}
        self.standard_skills['cet - 4'] = '大学英语四级'
        self.standard_skills['cet - 6'] = '大学英语六级'
        self.standard_skills['cet4'] = '大学英语四级'
        self.standard_skills['cet6'] = '大学英语六级'
        self.standard_skills['英语 4 级'] = '大学英语四级'
        self.standard_skills['英语 6 级'] = '大学英语六级'

    async def certificate_nor(self, input_skill: str):
        input_skill = input_skill.replace('|', ' ').replace(',', ' ').replace('，', ' ').replace('，', ' ')
        input_skill = re.sub(r'\s+', ' ', input_skill.strip())
        input_skill_list = input_skill.strip().lower().split(' ')
        if len(input_skill_list) < 2:
            input_skill_list = input_skill.strip().split(',')
            if len(input_skill_list) < 2:
                input_skill_list = input_skill.strip().split('/')

        result = []
        for input_skill_i in input_skill_list:
            mask = self.df['别名'].str.split(',').apply(lambda x: input_skill_i in x)
            df_1 = self.df[mask]
            if not df_1.empty:
                result.append(df_1.iloc[0, 2])
            else:
                input_skill_new = self.cut(input_skill_i)
                #input_skill_new = input_skill_i
                words_list = list(self.standard_skills.keys())
                match, score, _ = process.extractOne(input_skill_new, words_list, scorer=fuzz.token_set_ratio)
                if score > 90:
                    result.append(self.standard_skills[match])
                    #print(self.standard_skills[match])
                    result.append(input_skill_i)
                elif '证' in input_skill_i or '级' in input_skill_i:
                    result.append(input_skill_i)
        return list(set(result))

    async def process_certificate(self,key, value):
        result=await self.certificate_nor(value)
        return {'CERTIFICATE_NAME':result}

#c=CertificateNormalizer()
#print(c.certificate_nor('toefl'))
