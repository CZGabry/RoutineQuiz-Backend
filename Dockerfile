# Use an official Python runtime as a base image
FROM python:3.10.0

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install system dependencies for PyODBC
RUN apt-get update && apt-get install -y unixodbc-dev gnupg2 curl apt-transport-https

# Download and install the Microsoft ODBC Driver for SQL Server (Debian)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Expose port 5050 to the host
EXPOSE 5050

# Define environment variable to tell flask to run in development mode
ENV FLASK_ENV=development

# Run main.py when the container launches
CMD ["python", "main.py"]
