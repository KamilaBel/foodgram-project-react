FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV APP_HOME=/var/www/foodgram

# Create the appropriate directories
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
COPY requirements.txt $APP_HOME
RUN pip install --no-cache-dir -r requirements.txt

# Copy startup file
COPY entrypoint.sh $APP_HOME
RUN chmod +x entrypoint.sh
