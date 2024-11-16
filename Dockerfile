# Use a lightweight Python image compatible with Raspberry Pi
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port Flask will run on
EXPOSE 5001

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]