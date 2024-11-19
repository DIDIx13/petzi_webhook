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
    PETZI_SECRET=your_complete_petzi_secret_here
    ```

    > **Note:** Replace `your_secret_key_here` and `your_complete_petzi_secret_here` with your actual secrets.

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

### **1. Simulate Sending a Webhook:**

- **Using the Web Interface:**
  
  1. Navigate to [http://localhost:5000](http://localhost:5000).
  2. Enter the target webhook URL (e.g., [Webhook.site](https://webhook.site/)).
  3. Optionally enter a secret or use the default provided.
  4. Click **"Send Webhook"** to dispatch a simulated webhook.

### **2. Handle Incoming Webhooks:**

- The `/webhook` endpoint listens for incoming webhooks.
- The application verifies the authenticity of the request using HMAC signatures.
- Upon successful verification, it extracts the data and persists it to the PostgreSQL database.

## **Testing**

You can test the webhook handling functionality using either the built-in simulator or `curl`. Below are detailed instructions for both methods.

### **1. Testing with the Webhook Simulator**

The application provides a built-in simulator (`petzi_simulator.py`) to send test webhooks.

#### **Steps:**

1. **Ensure Your Services Are Running:**

    Make sure that both the `web` and `db` services are up and running.

    ```bash
    docker-compose ps
    ```

    **Expected Output:**

    ```
    Name                     Command               State           Ports         
    ------------------------------------------------------------------------
    petzi_webhook-db-1       docker-entrypoint.sh   Up      0.0.0.0:5432->5432/tcp
    petzi_webhook-web-1      flask run --host=0.... Up      0.0.0.0:5000->5000/tcp
    ```

2. **Send a Webhook Using the Simulator:**

    Open a new terminal window and navigate to the project directory.

    ```bash
    python petzi_simulator.py http://localhost:5000/webhook your_complete_petzi_secret_here
    ```

    > **Note:** Replace `your_complete_petzi_secret_here` with the `PETZI_SECRET` you defined in your `.env` file.

    **Expected Output:**

    ```
    Request successful. Response: {"message": "Webhook received and data persisted."}
    ```

3. **Verify the Database Entry:**

    Connect to the PostgreSQL database to verify that the webhook data has been stored.

    ```bash
    docker-compose exec db psql -U postgres -d petzi_webhook
    ```

    In the `psql` prompt, run:

    ```sql
    SELECT * FROM ticket;
    ```

    **Expected Output:**

    ```
     id |      number      |      type      |      title      |   category   | event_id |      event      | cancellation_reason |       generated_at       |    promoter     | price_amount | price_currency | buyer_role | buyer_first_name | buyer_last_name | buyer_postcode 
    ----+------------------+----------------+------------------+--------------+----------+-----------------+---------------------+--------------------------+------------------+--------------+----------------+------------+-------------------+------------------+-----------------
      1 | ABCD1234EFGH     | online_presale | Test To Delete   | Prélocation  |    54694 | Test To Delete  |                     | 2024-09-04 10:21:21+00   | Case à Chocs     |         25.00 | CHF            | customer   | Jane              | Doe              | 1234
    (1 row)
    ```

4. **Monitor Logs for Confirmation:**

    You can also monitor the `web` service logs to see detailed processing information.

    ```bash
    docker-compose logs web
    ```

    **Look for Entries Similar to:**

    ```
    INFO:__main__:Received webhook request
    INFO:__main__:Webhook data: {'event': 'ticket_created', ...}
    INFO:__main__:Ticket ABCD1234EFGH saved to database
    ```

### **2. Testing with `curl`**

If you prefer using `curl` to send webhooks, follow the steps below. Note that you'll need to generate a valid HMAC signature to authenticate the request.

#### **Prerequisites:**

- Make sure you have Python installed to generate the HMAC signature.

#### **Steps:**

1. **Generate HMAC Signature:**

    Create a Python script (e.g., `generate_signature.py`) to generate the required HMAC signature.

    ```python
    import hmac
    import hashlib
    import time

    def generate_signature(secret, body):
        timestamp = str(int(time.time()))
        body_to_sign = f"{timestamp}.{body}".encode('utf-8')
        digest = hmac.new(secret.encode(), body_to_sign, hashlib.sha256).hexdigest()
        signature = f"t={timestamp},v1={digest}"
        return signature

    if __name__ == "__main__":
        secret = "your_complete_petzi_secret_here"  # Replace with your PETZI_SECRET
        body = '''
        {
            "event":"ticket_created",
            "details":{
                "ticket":{
                    "number":"TEST12345678",
                    "type":"online_presale",
                    "title":"Curl Test Ticket",
                    "category":"Prélocation",
                    "eventId":12345,
                    "event":"Curl Test Event",
                    "cancellationReason":"",
                    "generatedAt": "2024-09-04T10:21:21.925529+00:00",
                    "sessions":[
                        {
                            "name":"Curl Session",
                            "date":"2024-01-27",
                            "time":"21:00:00",
                            "doors":"21:00:00",
                            "location":{
                                "name":"Case à Chocs",
                                "street":"Quai Philipe Godet 20",
                                "city":"Neuchatel",
                                "postcode":"2000"
                            }
                        }
                    ],
                    "promoter":"Case à Chocs",
                    "price":{
                        "amount":"25.00",
                        "currency":"CHF"
                    }
                },
                "buyer":{
                    "role":"customer",
                    "firstName":"John",
                    "lastName":"Smith",
                    "postcode":"5678"
                }
            }
        }
        '''
        signature = generate_signature(secret, body)
        print(signature)
    ```

    Run the script to get the signature:

    ```bash
    python generate_signature.py
    ```

    **Example Output:**

    ```
    t=1701305600,v1=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
    ```

2. **Send the Webhook with `curl`:**

    Use the generated signature to send the webhook.

    ```bash
    curl -X POST http://localhost:5000/webhook \
      -H "Content-Type: application/json" \
      -H "Petzi-Signature: t=1701305600,v1=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890" \
      -d '{
          "event":"ticket_created",
          "details":{
              "ticket":{
                  "number":"TEST12345678",
                  "type":"online_presale",
                  "title":"Curl Test Ticket",
                  "category":"Prélocation",
                  "eventId":12345,
                  "event":"Curl Test Event",
                  "cancellationReason":"",
                  "generatedAt": "2024-09-04T10:21:21.925529+00:00",
                  "sessions":[
                      {
                          "name":"Curl Session",
                          "date":"2024-01-27",
                          "time":"21:00:00",
                          "doors":"21:00:00",
                          "location":{
                              "name":"Case à Chocs",
                              "street":"Quai Philipe Godet 20",
                              "city":"Neuchatel",
                              "postcode":"2000"
                          }
                      }
                  ],
                  "promoter":"Case à Chocs",
                  "price":{
                      "amount":"25.00",
                      "currency":"CHF"
                  }
              },
              "buyer":{
                  "role":"customer",
                  "firstName":"John",
                  "lastName":"Smith",
                  "postcode":"5678"
              }
          }
      }'
    ```

    **Expected Output:**

    ```json
    {
      "message": "Webhook received and data persisted."
    }
    ```

3. **Verify the Database Entry:**

    Connect to the PostgreSQL database to verify that the webhook data has been stored.

    ```bash
    docker-compose exec db psql -U postgres -d petzi_webhook
    ```

    In the `psql` prompt, run:

    ```sql
    SELECT * FROM ticket;
    ```

    **Expected Output:**

    ```
     id |      number      |      type      |        title         |   category   | event_id |       event       | cancellation_reason |      generated_at       |    promoter     | price_amount | price_currency | buyer_role | buyer_first_name | buyer_last_name | buyer_postcode 
    ----+------------------+----------------+-----------------------+--------------+----------+-------------------+---------------------+-------------------------+------------------+--------------+----------------+------------+-------------------+------------------+-----------------
      2 | TEST12345678     | online_presale | Curl Test Ticket      | Prélocation  |    12345 | Curl Test Event   |                     | 2024-09-04 10:21:21+00  | Case à Chocs     |         25.00 | CHF            | customer   | John              | Smith            | 5678
    (1 row)
    ```

4. **Monitor Logs for Confirmation:**

    You can also monitor the `web` service logs to see detailed processing information.

    ```bash
    docker-compose logs web
    ```

    **Look for Entries Similar to:**

    ```
    INFO:__main__:Received webhook request
    INFO:__main__:Webhook data: {'event': 'ticket_created', ...}
    INFO:__main__:Ticket TEST12345678 saved to database
    ```

## **Deployment**

### **Using GitHub Actions**

The GitHub Actions workflow builds and pushes the Docker image to DockerHub, then deploys the services using Docker Compose.

The image is available at [didix13/petzi_webhook](https://hub.docker.com/r/didix13/petzi_webhook)

### **Manual Deployment**

Alternatively, you can manually build and run the Docker containers:

```bash
docker-compose up --build
```

## **Security Considerations**

- **Secret Management**: Secrets are managed using environment variables and GitHub Secrets.
- **Signature Verification**: Incoming webhook requests are verified using HMAC signatures to ensure authenticity.
- **Data Protection**: Sensitive information is not exposed in logs or frontend.

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.