import time
from multiprocessing import set_start_method
import aiohttp
import uvicorn
import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header, Depends
from concurrent.futures import ProcessPoolExecutor
import asyncio
import cupy as cp
from requests import Request
from resume_logger import logger
token_init=os.getenv('TOKEN','f809754fbb342c780236798c1384ef75')
def load_model():
    import spacy
    if not spacy.require_gpu():
        logger.error("无法使用GPU推理")
    nlp = spacy.load("./model/model-best")
    return nlp
MAX_CONCURRENT_REQUESTS = 2
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

NUM_MODEL_COPIES = 2
executor = ProcessPoolExecutor(max_workers=NUM_MODEL_COPIES)

def verify_token(token:str=Header(...)):
    try:
        if token.lower()!=token_init:
            raise HTTPException(status_code=401, detail=f"无效token")
        return {'token': token}
    except Exception as e:
        logger.error('token错误:',e)
app = FastAPI()

@app.middleware("http")
async def limit_concurrent_requests(request: Request, call_next):
    async with semaphore:
        return await call_next(request)

try:
    set_start_method('spawn')
except RuntimeError:
    pass
class TextRequest(BaseModel):
    text:dict
"""
class ConfigRequest(BaseModel):
    num_model: int

@app.post("/set_config/")
async def set_config(config: ConfigRequest):
    global NUM_MODEL_COPIES, executor

    if config.num_model< 1:
        raise HTTPException(status_code=400, detail="num_model 必须大于等于 1")

    NUM_MODEL_COPIES = config.num_model

    old_executor = executor
    old_executor.shutdown(wait=False)  

    executor = ProcessPoolExecutor(max_workers=NUM_MODEL_COPIES)

    return {
        "message": "配置已更新",
        "new_num_model_copies": NUM_MODEL_COPIES
    }
"""
async def async_inference(text,id_list):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_inference_on_gpu, text,id_list)
    return result

import threading

local_data = threading.local()


def split_overlap(s):
    t=len(s)//2+10
    #print(t)
    return [s[i:i+t+30] for i in range(0,len(s),t)]

def run_inference_on_gpu(text,id_list):
    try:
        if not hasattr(local_data, 'nlp') or local_data.nlp is None:
            local_data.nlp= load_model()
        docs = list(local_data.nlp.pipe(text, batch_size=50))
        text_all = {}
        for ids, doc in zip(id_list, docs):
            text_list = []
            for ent in doc.ents:
                text_list.append({ent.label_: ent.text})
            text_all[ids] = text_list
        #cp.get_default_memory_pool().free_all_blocks()
        return text_all
    except Exception as e:
        print(e)
        """
                text_all={}
                id_list_else=[]
                text_else=[]
                for ids,text_ in zip(id_list,text):
                    if not hasattr(local_data, 'nlp') or local_data.nlp is None:
                        local_data.nlp = load_model()
                    if len(text_)<2500:
                        id_list_else.append(ids)
                        text_else.append(text_)
                    docs = list(local_data.nlp.pipe(split_overlap(text_), batch_size=2))
                    for doc in docs:
                        text_list = []
                        for ent in doc.ents:
                            text_list.append({ent.label_: ent.text})
                        text_all[ids] = text_list
                for ids, doc in zip(id_list_else, text_else):
                    text_list = []
                    for ent in doc.ents:
                        text_list.append({ent.label_: ent.text})
                    text_all[ids] = text_list
                return text_all
                """
        return []


@app.post("/analyze")
async def analyze_text(data: TextRequest,token=Depends(verify_token)):
    try:
        start=time.time()
        data = data.text
        text = list(data.values())
        #text.replace('\\r', '').replace('：', ':').replace('\\n',' ')

        """提取到教育日期后再规范化日期"""

        #text=list(map(normalize_dates_in_text,data.values()))
        text=list(map(lambda x:x.replace('\\r', ' ').replace('：', ':').replace('\\n',' '),text))
        id_list = list(data.keys())
        #print(text[3])
        result = await async_inference(text,id_list)
        end=time.time()
        print('模型推理耗时：',end-start)
        if not result:
            raise HTTPException(status_code=402, detail="超出显存")
        url = "http://172.16.2.21:8005/process-text/"
        #url = "http://127.0.0.1:8005/process-text/"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'old':data,'new':result}) as response:
                if response.status == 200:
                    response1=await response.json()
                    return response1
                else:
                    return {"error": "Failed to process text", "status": response.status}
    except Exception as e:
        logger.error(f'模型推理出错:{e}')

if __name__=='__main__':
    uvicorn.run(
        app="model_analyse:app",
        host="0.0.0.0",
        port=8004,
        reload=False,
        workers=1
    )