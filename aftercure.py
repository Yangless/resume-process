import os
import time
from typing import Optional

import dateparser
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from process_date import normalize_dates_in_text
from res.certificate import CertificateNormalizer
from res.industry import IndustryMatcher
from res.major import MajorMatcher
from res.position import PositionNormalizer
from res.school import SchoolNormalizer
from res.chinese_500 import chinese_500_nor, LabelNormalizer
from res.city import city_nor
from res.skill_new import SkillNormalizer
from res.state_owned import company_nor
from concurrent.futures import ProcessPoolExecutor,as_completed
from contextlib import asynccontextmanager
from resume_logger import logger
"""
logger = logging.getLogger("resume_ner")
logger.setLevel(logging.INFO)
log_file=os.path.join('app.log')
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)
"""

#SKILL_RE=re.compile(r'\b(?:[A-Za-z]+\s?)+\b')

class Response(BaseModel):
    response: Optional[dict]

def process1( ids,text,text_list):
    certificate_nor = CertificateNormalizer()
    industry_nor = IndustryMatcher()
    major_nor=MajorMatcher()
    position_nor = PositionNormalizer()
    skill_nor = SkillNormalizer()
    label_nor=LabelNormalizer()
    school_nor=SchoolNormalizer()

    # skill_list=skill_nor.skill_nor(text)
    text_list_new = []
    certificate_list=[]
    major_list=[]
    position=[]
    industry=[]
    skill =[]
    year=0

    for text_splice in text_list:
        key = list(text_splice.keys())[0]
        value = list(text_splice.values())[0]
        if key == 'SCHOOL':
            school_json= school_nor.school_nor(value)
            if school_json['学校']:
                text_list_new.append({key: school_json['学校']})
            if school_json['标签']:
                text_list_new.append({'LABEL': school_json['标签']})
        elif key == 'COMPANY_NAME':
            try:
                #company_500 = chinese_500_nor(value)  # ['国家电网有限公司']
                company_state,state_owned = company_nor(value)  # ('xxx','央企')
                company_json=industry_nor.industry_nor(value)  #  {'公司':[],'行业':[]}
                company_label=label_nor.label_nor(value)  # {'公司': '北京三快科技有限公司', '标签': ['世界500强', '中国500强', '独角兽', '大厂经验']}
                #if company_500:
                    #text_list_new.append({key: value})
                    #text_list_new.append({'COMPANY_LABEL': '中国500强'})
                if company_state:
                    text_list_new.append({key: company_state})
                elif company_label['公司']:
                    text_list_new.append({key: company_label['公司']})
                elif company_json['公司']:
                    text_list_new.append({key: company_json['公司']})

                if state_owned:
                    text_list_new.append({'COMPANY_LABEL': state_owned})
                if company_json['行业']:
                    industry.extend(company_json['行业'])
                if company_label['标签']:
                    text_list_new.append({'COMPANY_LABEL': company_label['标签']})
            except Exception as e:
                print(e,value)

        elif key in ['CERTIFICATE_NAME','LANGUAGE','SCORE']:
            certificate = certificate_nor.certificate_nor(value)
            if certificate:
                certificate_list.extend(certificate)
        elif key=='MAJOR':
            major=major_nor.major_nor(value)
            if major:
                major_list.extend(major)
            else:
                major_list.append(value)
        #elif key == 'YEARS_OF_WORK_EXPERIENCE':
            #num = re.findall(r'(\d+|[一二三四五六七八九]+)年', value.replace(' ', ''))
            #if num:
                #text_list_new.append({key: num[0]})
        elif key in ['POSITION_TITLE']:
            position_dict=position_nor.position_nor(value)
            position.extend(position_dict['职位'])
            industry.extend(position_dict['行业'])
        elif key in ['DESIRED_INDUSTRY']:
            desired_industry=industry_nor.industry_nor1(value)
            if desired_industry:
                industry.extend(desired_industry)
        elif key in ['CURRENT_LOCATION','DESIRED_WORK_LOCATION']:
            city=city_nor(value)
            if city:
                text_list_new.append({'CURRENT_LOCATION':city})
        elif key =='SKILL_NAME':
            index=text.find(value)
            skill_list = skill_nor.skill_nor(text[index-30:index+len(value)+30],value)
            if skill_list:
                skill.extend(skill_list)
        elif key in ['EDUCATION_END_DATE','EDUCATION_START_DATE']:
            try:
                #print(value)
                year=normalize_dates_in_text(value.replace(' ',''))
                if '至今' in value:year=-1
            except Exception as e:
                logger.error(f'日期处理出错:{e}{value}')
        else:
            text_list_new.append({key:value})
    #print(skill_list)
    text_list_new.append({'SKILL_NAME':skill})
    text_list_new.append({'CERTIFICATE_NAME': list(set(certificate_list))})
    text_list_new.append({'MAJOR': list(set(major_list))})
    text_list_new.append({'POSITION': list(set(position))})
    text_list_new.append({'INDUSTRY': list(set(industry))})
    text_list_new.append({'EDUCATION_END_DATE': year})
    return  ids,text_list_new

def flatten_json(data):
    result = {}
    items = data
    try:
        for item in items:
            for key, value in item.items():
                if key not in result:
                    result[key] = []
                if isinstance(value, list):
                    result[key].extend(value)
                else:
                    result[key].append(value)
    except Exception as e:
        logger.error(f'合并出错{e}')
    return result

@asynccontextmanager
async def lifespan(app: FastAPI):
    global process_pool, thread_pool
    #thread_pool = ThreadPoolExecutor(max_workers=20)
    process_pool = ProcessPoolExecutor(max_workers=20)

    yield
    if process_pool is not None:
        process_pool.shutdown(wait=True)
        process_pool = None


app = FastAPI(lifespan=lifespan)

@app.post("/process-text/",response_model=Response)
async def process_text(data_all:dict):
    try:
        data=data_all['old']

        time_start=time.time()
        text_all = data_all['new']
        #print(text_all)
        #print(text_all.items())
        futures=[process_pool.submit(process1, ids,data[ids],text_list) for ids,text_list in text_all.items()]

        test_response={}
        for future in as_completed(futures):
            #print(future.result())
            ids,text_list_new = future.result()
            text_list_flatten=flatten_json(text_list_new)
            a2bmap={'LABEL':'schoolLabelArray','COMPANY_LABEL':'corpLabelArray','MAJOR':'majorArray',
             'SCHOOL':'schoolArray','SKILL_NAME':'skillArray','CERTIFICATE_NAME':'certificateArray',
             'POSITION':'postNameArray','COMPANY_NAME':'corpNameArray','INDUSTRY':'industryArray','CURRENT_LOCATION':'workPlaceArray',
                    'EDUCATION_END_DATE':'graduationYear'}
            text_list_map={a2bmap[key]:list(set(value)) for key,value in text_list_flatten.items() if key in a2bmap}
            text_list_map['resumeContent']=''
            if text_list_map['graduationYear']:
                text_list_map['graduationYear'] = text_list_map['graduationYear'][0]
            test_response[ids]=text_list_map

        time_end = time.time()
        print(f'模型后处理耗时:{time_end-time_start}')
        logger.info(f'模型后处理耗时:{time_end-time_start}')
        return {"response":test_response}
    except Exception as e:
        logger.error(f'{e}')
        #raise HTTPException(status_code=500, detail=str(e))

if __name__=='__main__':

    uvicorn.run(
        app="aftercure:app",
        host="0.0.0.0",
        port=8005,
        reload=False,
        workers=1
    )



