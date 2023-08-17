# Week 2 - Orchestrating Containers with ECS
This lab walks you through 
- creating a dockerhub account and repository
- pushing to the image repository
- creating a standalone ECS Task
- creating a highly available ECS Task

## 0 - Open AWS CloudShell
- Follow the [instructions here](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html) to open AWS CloudShell. Using CloudSheel will prevent working with AWS Access Keys.

## 1 - Clone Repo
1. In AWS CloudShell, clone the workshop repository with the command below
  
    ```
    git clone https://github.com/kordaralabs/free-containers-workshop.git
    cd free-containers-workshop
    ```
    
2. Change directory to `2-orchestrating-containers-with-ecs`

    `cd 2-orchestrating-containers-with-ecs`

## 2 - Setup AWS Infrastructure for ECS
### 2.1 - Create CloudFormation Stack
Use CloudFormation to setup the ECS Cluster, ECR repository, VPC, Subnets, Security Groups, Load Balancer and EC2 instance for the ECS Cluster. It will take a couple of minutes for the resources to be created.

`aws cloudformation create-stack --stack-name infra --template-body file://template.yaml --capabilities CAPABILITY_NAMED_IAM --region us-west-1`

### 2.2 - Get all Ids, resource names and ARNs of resources created by CloudFormation
This command will be used multiple times in this guide. The output can be copied to a temporary file for reference, if you do not want to run it multiple times. 

`aws cloudformation list-exports --query 'Exports[*].[Name,Value]' --output table`


Optional: Open the `infra` Stack in [CloudFormation](https://us-west-1.console.aws.amazon.com/cloudformation/home?region=us-west-1#/stacks/) to see the resources.

## 3 - Push Image to ECR 
Get the ID of your AWS Account for use in the subsequent commands with `<ACCOUNT ID>` placeholder

  `aws sts get-caller-identity --query Account --output text`

### 3.1 - Login to ECR on Local Terminal
AWS CloudShell does not currently support Docker, so the container images cannot be built or pushed from it. The image will have to be pushed from your local computer/workstation.

- `CLOUDSHELL`: Run the AWS command below in CloudShell to get the credentials for the ECR respository

  `aws ecr get-login-password --region us-west-1`

- `LOCAL COMPUTER/WORKSTATION`: Open a terminal on your local workstation, and login with the credentials returned from the previous command. When asked for `password`, copy and paste the credentials from CloudShell. Ensure to replace `<ACCOUNT ID>` with the AWS Account ID.

  `docker login --username AWS <ACCOUNT ID>.dkr.ecr.us-west-1.amazonaws.com`

  Alternatively, use the command below that specifies the credentials as part of the argument instead of the hidden prompt.

  `docker login --username AWS <ACCOUNT ID>.dkr.ecr.us-west-1.amazonaws.com --password <ECR credentials from CloudShell>`

### 3.2 - Change image name
The command below gives an alternative name to the `flask-app` container image.

`docker tag flask-app <ACCOUNT ID>.dkr.ecr.us-west-1.amazonaws.com/flask-app`

### 3.3 - Push image to the repository
Push the image to the ECR repository

`docker push <ACCOUNT ID>.dkr.ecr.us-west-1.amazonaws.com/flask-app`

## 4 - Create ECS Task Definition
Task Definition is a template for ECS to run tasks with. 

### 4.1 - Replace placeholders in the `task-definition.json` file
- Replace `<ACCOUNT ID>` with the actual `Account ID` from Step `3`

  ```
  ...
  "name": "flask-app",
  "image": "<ACCOUNT ID>.dkr.ecr.us-west-1.amazonaws.com/flask-app", <------------------ here
  "essential": true
  ...
  ```       

- Set the Task Execution Role ARN to the value of `TaskExecRoleArn` from Step `2.2`

  ```
  ...
  "family": "flask-app",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT ID>:role/<Role Name>",   <------------------ here
  "networkMode": "awsvpc",
  ...
  ```

### 4.2 - Create Task Definition
- Create the Task Definition and store the ARN for steps `5` and `6` 
  
  ```
  TD_ARN=$(aws ecs register-task-definition --cli-input-json file://task-definition.json \
    --query 'taskDefinition.taskDefinitionArn' --output text) && echo $TD_ARN
  ```

## 5 - Create Standalone Task and test it
Subnet Ids, Security Group Id and the Task Definition ARN are needed to create the standalone ECS Task. 

### 5.1 - Set required variables
The Task Definition ARN (`TD_ARN`) has already been set in step `4.2`. However, other variables need to set from the table in step `2.2`

 `SG_ID=<Set to value of AllowHTTPSG>`

 `SUBNET_1=<Set to value of SubnetUSWest1a>`

 `SUBNET_2=<Set to value of SubnetUSWest1c>`

### 5.2 - Create standalone Task
Create the Task with the command below and store the `TASK_ARN` for later use

  ```
  TASK_ARN=$(aws ecs run-task --cluster default --task-definition $TD_ARN --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_1],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
  --query 'tasks[0].taskArn' --output text) && echo $TASK_ARN
  ```

### 5.3 - Test the standalone Task
- Test the task in a browser by visiting its public IP

  ```
  NETWORK_INTERFACE_ID=$(aws ecs describe-tasks --cluster default --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
  PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $NETWORK_INTERFACE_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text) && echo $PUBLIC_IP
  ```

- Visit the public IP of the Task on port 8080 that the application runs on `<Public IP>:8080` or use curl like in the example below

  `curl $PUBLIC_IP:8080`

### 5.4 - Stop standalone Task
Delete the Standalone ECS Task
 
`aws ecs stop-task --cluster default --task $TASK_ARN`

## 6 - Create Highly Available Service using ECS Service and Load Balancers
### 6.1 - Set required variables
Set the Target Group ARN in a variable. The Target Group ARN is needed to setup to a Load Balancer for the ECS Service.

`TG_ARN=<Set to value of TgARN>`

### 6.2 - Create the ECS Service
Create ECS Service using previously created Load Balancer

  ```
  aws ecs create-service --service-name flask-app-service --cluster default \
  --task-definition $TD_ARN --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_1],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=$TG_ARN,containerName="flask-app",containerPort=8080
  ```
  
### 6.3 - Test ECS Service 
Test the ECS Service by visiting the Load Balancer URL in a browser. The URL is the value of `LbDnsName` from the table in Step `2.2`

## 7 - Cleanup
- Delete the ECS Service. `--force` allows deleting a service without scaling the tasks to 0
  `aws ecs delete-service --cluster default --service flask-app-service --force`

- Delete Images in the ECR repository
  
  `aws ecr delete-repository --repository-name flask-app --force`

- Deregister and delete each Task Definition revision
  - List all revisions
  
    `aws ecs list-task-definitions --family-prefix flask-app`

  - Deregister each revision number, replace `<revision number>` with the Task Definition revision number
  
    `aws ecs deregister-task-definition --task-definition flask-app:<revision number>`

  - Delete the Task Defintion revision, replace `<revision number>` with the Task Definition revision number
  
    `aws ecs delete-task-definitions --task-definition flask-app:<revision number>`
 
- Delete CloudFormation stack

  `aws cloudformation delete-stack --stack-name infra`

  Wait for a couple of minutes and then use the command below to verify if the Cloudformation stcak has been deleted succesfully

  `aws cloudformation describe-stacks --stack-name infra`

  Deletion is successful if you get the error below

  `An error occurred (ValidationError) when calling the DescribeStacks operation: Stack with id infra does not exist` 