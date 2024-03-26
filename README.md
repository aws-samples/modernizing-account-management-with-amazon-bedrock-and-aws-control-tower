### AWS Lambda Functions and Knowledge Base used in Account factory for Terraform with Amazon Bedrock Agents

---

#### Overview
This README documents two AWS Lambda functions designed for automating AWS account setup and customization using Amazon Bedrock and Account Factory for Terraform (AFT), along with a Knowledge Base (KB) used by these Lambdas. This solution follows AWS security reference architecture(https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/architecture.html), and can be utilized to create AWS account types such as security tooling, infrastructure, workload accounts, and deploy respective AWS services for each type of AWS account. This blog focuses on creating the security tooling account and deployment of the recommended AWS security services.

#### Solution Overview
- The user utilizes the bedrock agent chat console to input their AWS account creation requirements. For instance, the user might specify, "Create an AWS Account for Security Tooling". The agent is configured with instructions and bedrock knowledge base to customize and create an AWS account via Account Factory for Terraform. 
- On receiving the above example request, the agent queries a Bedrock Knowledge Base predefined with recommended AWS security services for Security Tooling AWS account. The agent presents these security services to the user. The user inputs a subset or all of the recommended security services.
- Next, the agent collects user information for account creation. Based on the AWS services the user selects, the agent passes the service information to an action group that invokes the  Lambda function(Account customization lambda). This function retrieves approved Terraform module configurations from a predefined Knowledge Base, uses bedrock LLM model to construct modular terraform code, and pushes the terraform code to AFT account customization repository(learn-terraform-aft-account-customizations).
- Before moving to the next step for account creation with the user selected AWS security services, the agent asks the user to confirm/update terraform code that was published to the AFT account customization repo.
- Once the agent receives user confirmation, the agent passes the the information to another action group that invokes a lambda function(Account creation Lambda) that publishes the AWS account creation terraform module to AFT account request repository (learn-terraform-aft-account-request) and AWS Control Tower Account Factory for Terraform (AFT) pipeline is triggered.

Solution Workflow:
The below diagram pictorially represents how the solution works.
 ![Workflow]([Solution-workflow.png](https://github.com/aws-samples/modernizing-account-management-with-amazon-bedrock-and-aws-control-tower/blob/main/Solution-workflow.png))
 
See an example illustrative chat, showcasing how users can interact with Bedrock agent to seamlessly create a Security-tooling account: 
![Bedrock agent]([Bedrock-agent-console.png](https://github.com/aws-samples/modernizing-account-management-with-amazon-bedrock-and-aws-control-tower/blob/main/Bedrock-agent-console.png))

#### Account Creation Lambda
- **Description**: Automates AWS account creation by appending new Terraform modules to a GitHub repository.
- **Environment Variables**:
  - `GITHUB_TOKEN`: Token for GitHub API authentication.
  - `KNOWLEDGE_BASE_ID`: ID of created Knowledge base
- **Dependencies**: Python 3.x, `requests` library.
- **Logical Flow**:
  1. Receives an event with account details.
  2. Extracts parameters and constructs a Terraform module snippet.
  3. Checks GitHub repository for existing `main.tf` file.
  4. Appends new Terraform module to existing content.
  5. Encodes updated content and commits to GitHub.
  6. Returns success or error message.

#### Account Customization Lambda
- **Description**: Generates and commits Terraform configurations for custom AWS services to a GitHub repository.
- **Environment Variables**:
  - `GITHUB_TOKEN`: Token for GitHub API authentication.
- **Dependencies**: Python 3.x, `boto3`, `requests`, `logging`, `base64` libraries.
- **Logical Flow**:
  1. Receives an event with customization details.
  2. Splits and processes AWS service requests.
  3. Retrieves Terraform module definitions from the KB.
  4. Invokes Bedrock model to generate Terraform and README contents.
  5. Commits generated Terraform configuration and README to GitHub.
  6. Returns success message with GitHub URLs or error information.

#### Add the Action groups to Agent:

- Provide a name for each of your action group and describe what the action does in the Description for action groups.
- In Select Lambda function, for both your action groups choose the appropriate Lambda functions that you created in AWS Lambda. The Lambda function provides the business logic that is carried out upon invoking the action. Choose the version of the function to use. For more information, see Action group Lambda functions
- In Select API schema, provide a link to the Amazon S3 URI of the schema with the API description, structure, and parameters for the action group. APIs manages the logic for receiving user inputs and triggering the Lambda functions for account creation and customization. The API should be designed to handle various tasks, such as validating user inputs, initiating the Terraform module creation process, and monitoring the status of account provisioning. For more information, see Action group OpenAPI schemas.
- Select Add another Action group to set up another action group for your agent. When you are done adding action groups, select Next.


#### Knowledge Base (KB)
- **Description**: A structured repository containing AWS service and Terraform module information.
- **Structure**: JSON format categorizing services and modules.
- **Configure Knowledge Base**: Configuring a Knowledge Base (KB) enables your Bedrock agents to access a repository of information for AWS account provisioning. Follow these steps to set up your KB:
  1. Access the Amazon Bedrock Console: Log in and go directly to the 'Knowledge Base' section. This is your starting point for creating a new KB.
  2. Name Your Knowledge Base: Choose a clear and descriptive name that reflects the purpose of your KB, such as "AWS Account Setup KB."
  3. Select an IAM Role: Assign a pre-configured IAM role with the necessary permissions. 
  4. Define the Data Source: Upload a JSON file to an S3 bucket with encryption enabled for security. This file should contain a structured list of AWS services and Terraform modules. For the JSON structure, use the example provided in this repository
  5. Choose the Default Embeddings Model: For most use cases, the Amazon Bedrock Titan G1 Embeddings - Text model will suffice. It's pre-configured and ready to use, simplifying the process.
  6. Opt for the Managed Vector Store: Allow Amazon Bedrock to create and manage the vector store for you in Amazon OpenSearch Service.
  7. Review and Finalize: Double-check all entered information for accuracy. Pay special attention to the S3 bucket URI and IAM role details.


#### Updating and Maintenance
- **Lambda Functions**:
  - Regularly update dependencies and environment variables.
  - Monitor Lambda logs for troubleshooting.
- **Knowledge Base**:
  - Regularly update with new AWS services and modules.
  - Validate JSON structure after updates.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

