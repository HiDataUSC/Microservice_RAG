# Microservice_RAG

Global variables:
- saved in .env file

Navigate to /path/to/Microservice_RAG

Install:
1. `conda create -n test_env python=3.11`
2. `conda activate test_env`
3. `pip install -r path/to/requirements.txt`

Run test for Generate microservice:
1. run `./tests/generation/generation_test.sh`

To run the website:
1. Navigate to `frontend/chatflow`
2. open terminal 1 run `python -m tests.api_server`
3. open terminal 2 run `npm run dev`

manage vectorized db:
`python -m services.common.vectorstore_action`

To create lambda deployment package (layer):
navigate to services folder for example `services/Text_Generation`
follow the tutorial: https://www.youtube.com/watch?v=grRW1Z_C9vw

