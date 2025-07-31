FROM python:3.12 AS builder

WORKDIR /app

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

COPY . .

FROM builder as resume-ner

COPY ./model_analyse.py /app/
EXPOSE 8004
CMD ["uvicorn", "model_analyse:app", "--host", "0.0.0.0", "--port", "8004"]

FROM builder as aftercure
COPY ./aftercure.py /app/
EXPOSE 8005
CMD ["uvicorn", "aftercure:app", "--host", "0.0.0.0", "--port", "8005"]