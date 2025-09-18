FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY README.md ./

#install poetry
RUN pip install poetry==2.1.4

# Install Poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
# Expose the port Streamlit runs on
EXPOSE 8501

# Run Streamlit
CMD ["poetry", "run", "streamlit", "run", "src/simulator.py", "--server.address", "0.0.0.0"]