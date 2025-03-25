# Use a imagem base do Python
FROM python:3.9-slim

# Instala dependências necessárias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instala o Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Instala o ChromeDriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Copia o script para o contêiner
# COPY main.py /app/RE-FastscreenNovo
RUN mkdir /code

RUN chown -R 777 /code

# Define o diretório de trabalho
WORKDIR /code

# Instala as bibliotecas Python necessárias
RUN pip install --no-cache-dir selenium webdriver_manager

# Define a execução do script
# ENTRYPOINT ["python", "main.py"]
