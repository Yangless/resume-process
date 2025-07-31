

import asyncio
import time
from typing import Optional
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
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
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

async def process_company(key, value, company_nor, industry_nor, label_nor):
    try:
        company_state, state_owned = await company_nor(value)
        company_json = await industry_nor.industry_nor(value)
        company_label = await label_nor.label_nor(value)

        result = []
        if company_state:
            result.append({key: company_state})
        elif company_label['公司']:
            result.append({key: company_label['公司']})
        elif company_json['公司']:
            result.append({key: company_json['公司']})

        if state_owned:
            result.append({'COMPANY_LABEL': state_owned})
        if company_json['行业']:
            result.append({'INDUSTRY': company_json['行业']})
        if company_label['标签']:
            result.append({'COMPANY_LABEL': company_label['标签']})

        return result
    except Exception as e:
        print(e, value)


async def process1( ids,text,text_list):
    certificate_nor = CertificateNormalizer()
    industry_nor = IndustryMatcher()
    major_nor=MajorMatcher()
    position_nor = PositionNormalizer()
    skill_nor = SkillNormalizer()
    label_nor=LabelNormalizer()
    school_nor=SchoolNormalizer()

    skill_list=await skill_nor.skill_nor(text)

    year=0
    tasks = []
    for text_splice in text_list:
        key = list(text_splice.keys())[0]
        value = list(text_splice.values())[0]

        if key == 'SCHOOL':
            tasks.append(asyncio.create_task(school_nor.process_school(key, value)))
        elif key == 'COMPANY_NAME':
            tasks.append(process_company(key, value, company_nor, industry_nor, label_nor))
        elif key in ['CERTIFICATE_NAME', 'LANGUAGE', 'SCORE']:
            tasks.append(asyncio.create_task(certificate_nor.process_certificate(key, value)))
        elif key == 'MAJOR':
            tasks.append(asyncio.create_task(major_nor.process_major(key,value)))
        elif key in ['POSITION_TITLE']:
            tasks.append(asyncio.create_task(position_nor.process_position(key,value)))
        elif key in ['DESIRED_INDUSTRY']:
            tasks.append(asyncio.create_task(industry_nor.process_industry1(key,value)))
        elif key in ['EDUCATION_END_DATE','EDUCATION_START_DATE']:
            try:
                year=normalize_dates_in_text(value.replace(' ',''))
                if '至今' in value:year=-1
            except Exception as e:
                logger.error(f'日期处理出错:{e}{value}')
    results = await asyncio.gather(*tasks)
    text_list_new= [{'EDUCATION_END_DATE': year}, {'SKILL_NAME': skill_list}]
    for x in results:
        if isinstance(x,list):
            text_list_new.extend(x)
        else :text_list_new.append(x)
    return ids, text_list_new

def wrapper(ids, text, text_list):
    return asyncio.run(process1(ids, text, text_list))

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
    global thread_pool
    thread_pool = ThreadPoolExecutor(max_workers=20)
    #process_pool = ProcessPoolExecutor(max_workers=20)

    yield
    if thread_pool is not None:
        thread_pool.shutdown(wait=True)
        thread_pool = None


app = FastAPI(lifespan=lifespan)

@app.post("/process-text/",response_model=Response)
async def process_text(data_all:dict):
    try:
        data=data_all['old']

        time_start=time.time()
        text_all = data_all['new']
        #print(text_all)
        #print(text_all.items())
        futures=[thread_pool.submit(wrapper, ids,data[ids],text_list) for ids,text_list in text_all.items()]
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
        print(f'总耗时:{time_end-time_start}')
        logger.info(f'总耗时:{time_end-time_start}')
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





