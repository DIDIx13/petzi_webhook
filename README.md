# Petzi Webhook Simulator

## **Overview**

This application simulates and handles Petzi webhooks. It verifies the authenticity of incoming webhook requests, extracts business information, and persists it to a PostgreSQL database. The application is containerized using Docker and orchestrated with Docker Compose.

## **Features**

- **Webhook Simulation:** Send simulated Petzi webhook requests to specified URLs.
- **Webhook Verification:** Verify the sender and origin of incoming webhook requests using HMAC signatures.
- **Data Persistence:** Store webhook data in a PostgreSQL database for future use.
- **Containerization:** Dockerized application with Docker Compose for easy deployment.
- **Automated Workflows:** GitHub Actions workflows for continuous integration and deployment.

## **Getting Started**

### **Prerequisites**

- Docker and Docker Compose installed
- GitHub account

### **Installation**

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/DIDIx13/petzi_webhook.git
    cd petzi_webhook
    ```

2. **Set Up Environment Variables:**

    Create a `.env` file in the root directory:

    ```dotenv
    # .env

    # Flask Secret Key
    SECRET_KEY=your_secret_key_here

    # Petzi Secret
    PETZI_SECRET=your_secret_key_here
    ```

3. **Build and Run with Docker Compose:**

    ```bash
    docker-compose up --build
    ```

4. **Apply Database Migrations:**

    In a new terminal:

    ```bash
    docker-compose exec web flask db migrate -m "Initial migration."
    docker-compose exec web flask db upgrade
    ```

5. **Access the Application:**

    Open [http://localhost:5000](http://localhost:5000) in your browser.

## **Usage**

1. **Simulate Sending a Webhook:**

    - Enter the target webhook URL (e.g., [Webhook.site](https://webhook.site/)).
    - Optionally enter a secret or use the default.
    - Click **"Send Webhook"**.

2. **Handling Incoming Webhooks:**

    - The `/webhook` endpoint listens for incoming webhooks.
    - Verify the authenticity of the request.
    - Extract and persist the data to the database.

## **Deployment**

### **Using GitHub Actions**

The GitHub Actions workflow builds and pushes the Docker image to DockerHub, then deploys the services using Docker Compose.

### **Manual Deployment**

Alternatively, you can manually build and run the Docker containers:

```bash
docker-compose up --build
```