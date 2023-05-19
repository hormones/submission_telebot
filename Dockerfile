FROM python:3.10-slim-buster

# Set the working directory and copy the project files from the Git repository to the image
WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get install -y sqlite3

RUN git clone https://github.com/hormones/submission_telebot .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry command
CMD ["python", "main.py"]
