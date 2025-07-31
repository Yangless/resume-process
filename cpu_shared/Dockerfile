FROM python:3.12 as builder

WORKDIR /app

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements_cpu.txt .
RUN pip install --no-cache-dir -r requirements_cpu.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

RUN pip install --no-cache-dir spacy-pkuseg -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
COPY . .

FROM builder as resume-ner

COPY ./model_analyse_cpu.py /app/
EXPOSE 8004
CMD ["uvicorn", "model_analyse_cpu:app", "--host", "0.0.0.0", "--port", "8004"]

FROM builder as aftercure
COPY ./aftercure.py /app/
EXPOSE 8005
CMD ["uvicorn", "aftercure:app", "--host", "0.0.0.0", "--port", "8005"]