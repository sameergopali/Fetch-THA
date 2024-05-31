# Fetch Rewards - Data Engineering Challenge

## Table of Contents
1. [Task](#task)
2. [How to Run](#how-to-run)
3. [Design Questions](#design-question)
4. [Questions](#questions)
5. [Next Steps](#next-steps)
### Task
The task is to create a data pipeline that fetches messages from an AWS SQS queue, processes these messages by masking user_id and ip fields, stores the processed records into a PostgreSQL database.

### How to Run
To run the data pipeline, follow these steps:

1. Clone the repository:

```bash
git clone 
cd fetch-tha
```

You will need the following installed on your local machine
1. docker -- docker [install guide](https://docs.docker.com/get-docker/)
2. Psql - [install](https://www.postgresql.org/download/)


Install python dependencies
```bash
pip install -r requirements.txt
```
3. Run docker containers:
```bash
docker compose up -d
```
4. Run main python program
```bash
python app/main.py
```
The main.py script contains the logic to continuously fetch, process, and store messages.

5. For Checking the final output, connect to postges and query the user_logins table
```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
password : postgres

select * from user_logins;
```

## Design question 
### How will you read messages from the queue?
I  processed messages in batches from the SQS queue with a batch size of 10. Processing in batches can reduce the number of requests to SQS and potentially improve performance and reduce costs as number of request is decreased, but it comes with tradeoffs. Handling failures and maintaining ordering becomes more complex with batch processing compared to single message processing. However, given the requirements of this assignment, I believe that batch processing with a reasonable batch size strikes a good balance between performance and complexity.
### What type of data structures should be used?
I have used Python dictionaries to store the JSON message data. Dictionaries provide efficient key-value lookup and are well-suited for working with JSON data. 
While creating a custom data object could have provided some benefits like data abstraction and better validation, I chose to keep the implementation simple by using dictionaries directly.
For this specific use case, where the message data structure is relatively simple and the primary focus is on processing and masking the data, I checked for the required keys in the message dictionary and perform necessary validations. This approach avoids the overhead of creating a custom class or object, making the implementation more straightforward.



### How will you mask the PII data so that duplicate values can be identified?

There are numerous ways like using encrpytion, hashing them or encoding to different format like base64. With encryption/encoding, it would be possible to reverse the masked message. For this task,  I have used  SHA-256 hashing for masking the data as it is a one-way function that produces a fixed-size output assuming that we don't want to PII to comprised. Hashing will also provide way to identify duplicate values as same hash is being produced and the number of hash collision is very small.

### What will be your strategy for connecting and writing to Postgres?
For writing data to PostgreSQL, I  used bulk inserts as we are processing batch of data. Bulk inserts can provide better performance compared to individual inserts.
Regarding the database connection strategy, since this is a single application writing to the database, I  used a single connection to PostgreSQL.  Using a single connection simplifies the implementation and avoids the overhead of managing a pool of connections.
If the application grows to involve multiple services or processes accessing the database concurrently, implementing a connection pooling mechanism would be a more appropriate strategy. Connection pooling can improve performance by reusing existing connections, reducing the overhead of establishing new connections for each request. 

### Where and how will your application run?
Since the sqs is not continously streaming the data,  the application run as a standalone application that is run once to process all the data in the queue. But depending on the specific requirements and constraints, it would be possible to deploy it in a containerized environment or also in serverless options like AWS Lambda.



## Questions

### How would you deploy this application in production?
To deploy in production we can use serveless function like lambda or use containarization which would provide easy portablity and scalability.We can implement a batch processing mechanism or stream process depending upon the need of the data analyst.


### What other components would you want to add to make this production-ready?
I would additionally implement central logging mechanisms like AWS Cloudwatch and integrate with a monitoring solution like Prometheus for checking service healths. I also consider needing CI/CD for pipeline for automated building/testing and deploying of the serice. I would also consider adding dead letter queue for handling messages that could not be processed.

### How can this application scale with a growing dataset.
To scale the application horizontally and handle increasing workloads, we can run multiple instances of the app behind a load balancer. By leveraging container orchestration platforms like Kubernetes, we can automatically scale the number of app instances based on resource utilization metrics or custom metrics related to message processing rates, queue depths, or other relevant factors.
For handling high-throughput scenarios, we could consider using a scalable message queue system like Apache Kafka instead of SQS. Kafka is designed for high-throughput, low-latency message processing and offers features like partitioning, replication, and fault-tolerance out of the box. However, this would require additional infrastructure and operational overhead compared to the managed SQS service.
As the dataset grows significantly, we can implement database sharding or partitioning strategies to distribute the data across multiple PostgreSQL nodes or instances. This can help distribute the read and write load across multiple databases, improving scalability and performance. Additionally, we can set up read replicas for the PostgreSQL database to improve read availability and further reduce the read load on the primary database instance.

### How can PII be recovered later on?
Instead of using hashing, if we want to PII to be recovered later on we can use encryption algorithm can be used in the future like AES-256 or RSA, which would help in decrypting the encrypted text, but given the decryption key is kept securely.

### What are the assumptions you made?
The assumptions I have made:
- The required database is created.
- The messages are structured and does not require additional validations, we can only check for the presence of the required keys in message for correct message format.
- The order of message does not matter.
- We require PII not to  be reversible so hashing is used, 
- The application is to be run as standalone application, so scheduling is not implemented.
- To handle incorrect message, we can simply remove them from queue.



### Next Steps:
- Write unit tests to validate the behavior of individual functions and methods. Cover edge cases
-  Validate incoming messages from the SQS queue to ensure they meet expected criteria and structure.
- Improve logging statements to provide more detailed information about the application's behavior and state.
- Refactor the application to support asynchronous processing messages to improve throughput and responsiveness.
- Improve error handling and implement retry mechanisms
- Implement different masking options like encryption.
- Build Docker images for the application.
- Implement configuration files (e.g., YAML, JSON) to store application settings, environment variables, and runtime parameters.