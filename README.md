# diploma-project

## Required OS and Additional Technologies:
- Linux VM / WSL with Ubuntu 22.04 LTS
- Docker
    - [Docker Engine](https://docs.docker.com/engine/) + [Docker Compose](https://docs.docker.com/compose/)
    - [or only Docker Desktop](https://docs.docker.com/desktop/)
- CUDA Toolkit:
    - "sudo apt install nvidia-cuda-toolkit"
    - [.deb package](https://developer.nvidia.com/cuda-downloads)
    - [or detailed installation](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- GCC and G++ Compilers:
    - "sudo apt install gcc g++"
- Git + Git LFS:
    - "sudo apt install git"
    - "curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash"
    - "sudo apt-get install git-lfs"
    - "git lfs install"
    - Install some model with "git clone ```link here```"

## Databases:
- PostgreSQL (Local in Docker):
  - Default PostgreSQL 16.X
  - PGvector Extension

## LLMs:
- [Leaderboard](https://huggingface.co/collections/open-llm-leaderboard/the-big-benchmarks-collection-64faca6335a7fc7d4ffe974a)
- [GGUF](https://huggingface.co/docs/hub/en/gguf) - quantization format (like "optimization" process).
- Instruct - fine-tuned models for understanding natural language instructions in the prompt.
- Llama 3:
  - [bartowski/8B-Instruct-GGUF](https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF)
  - [QuantFactory/8B-Instruct-GGUF](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF)
  - [meta-llama/8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)

## Embeddings:
  - [Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
  - [intfloat/multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large)
  - [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
  - [sentence-transformers/distiluse-base-multilingual-cased-v2](https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v2)
  - [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small)

## ASR / STT:
  - [About ASR / STT](https://huggingface.co/tasks/automatic-speech-recognition)
  - [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3)

## Backend:
- Python 3.10.x:
  - install requirements - in backend directory "python3 -m venv venv" then "pip install -r requirements.txt"
  - freeze requirements - in backend directory "pip freeze > requirements.txt"
- Requirements:
  - fastapi[all]
  - sqlalchemy[asyncio]
  - alembic
  - asyncpg
  - pyjwt[crypto]
  - llama-cpp-python:
    - create seperate venv ```python3 -m venv venv_llama``` (because version of dependencies can cause some bugs with GPU acceleration)
    - install or reinstall with ```CMAKE_ARGS="-DLLAMA_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir``` or ```CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir```
    - for server api inference - ```pip install llama-cpp-python[server]```
    - run server api inference - ```python3 -m llama_cpp.server --config_file <config_file or config file path>```
  - langchain langchain-community langchain_openai
  - transformers
  - sentence-transformers
  - faiss-cpu / faiss-gpu
  - argon2-cffi
  - sqladmin
  - langfuse (sdk + docker)
  - 

## Frontend:
- Python 3.10.x:
- Requirements:
  - streamlit extra-streamlit-components
  - httpx
  - pydantic[email] pydantic_settings
  - pyscaffold
  - pyinstrument
  - pyjwt[crypto]

## Need to do:
- временный выход - сделать аналог чат бота как в тг с выбором вариантов запроса
- понимание контекста истории сообщений
- ответ на несколько вопросов за один раз - возможно использовать чтоб модель генерила json с несколько cypher query
- добавить whisper large v3 - войс
- оценка ответов (положительно и негативно) - RLHF
- vue новая обертка - на жаксылыке
- новые примеры query - на еркежан
- миграция на микросервесную архитектуру
- добавление elasticsearch для поиска по быстрого поиска по названию частов их содержанию
- refresh token / block token
- Architecture (need mermaid chart)

Feature - Добавить chat history:
- возможно суммировать контекст всех сообщений чата, чтобы модель понимала из контекста вопросы.

Bug / Fix - Слишком большой response от Neo4j не влезает в context window модели Llama 3 8b (8192 токена максимум) - обычно случается в вопросах с госзакупками:
- Может возможно использовать RAG

Fix / Bug - В некоторых случаях, QA ответ модели может не опираться на context выданный neo4j и его попросту игнорирует - нужно чтоб ответ был больше болтливым:
- Возможно исправить qa_prompt (изменить его текстовку, добавить примеры как может выглядеть question-context-response для модели, изменить параметры модели именно только для qa_prompt)

Fix / Bug - Галлюцинации генерации Cypher Query (неверно создаёт иногда для маленьких запросов cypher query, а для больших и сложных запросов cypher query выдает попросту все неверные):
- возможное решение это создать больше примеров, изменить параметры модели, добавить валидацию и перегенерацию cypher query если он неверный, возможно сделать fine tuning