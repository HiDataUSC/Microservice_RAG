docker run --rm -v "$PWD":/var/task "public.ecr.aws/lambda/python:3.9" \
  /bin/sh -c "pip install -r requirements.txt -t ."

zip -r generation_lambda.zip ./*