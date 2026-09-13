FROM python:3.11-slim-bookworm

# Install ODBC driver for SQL Server (Debian 12 / Bookworm) using modern GPG keyring method
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -sSL https://packages.microsoft.com/config/debian/12/prod.list | sed 's/\[arch=amd64\]/[arch=amd64 signed-by=\/usr\/share\/keyrings\/microsoft-prod.gpg]/' > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
