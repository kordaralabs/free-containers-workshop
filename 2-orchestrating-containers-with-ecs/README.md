# Week 2 - Orchestrating Containers with ECS
This lab walks you through 
- creating a dockerhub account and repository
- pushing to the image repository
- creating a standalone ECS Task
- creating a highly available ECS Task

## 0 - Clone Repo
1. Open a terminal
2. Clone the workshop repository with the command below
  
    `git clone https://github.com/kordaralabs/free-containers-workshop.git`
    
    Alternatively, download the [ZIP here](https://github.com/kordaralabs/free-containers-workshop/archive/refs/heads/main.zip) if you don't have git installed. Then, navigate to the directory of the unzipped file in the terminal
    
3. Change directory to `2-orchestrating-containers-with-ecs`

    `cd 2-orchestrating-containers-with-ecs`

## 1 - Dependencies
### 1.1 - Install AWS CLI
Follow instructions here to install the AWS CLI

### 1.2 - Setup AWS User for the CLI or User CloudShell

## 2 - Setup an Image Respository
### - DockerHub
1. Sign up for Dockerhub: [Dockerhub](https://hub.docker.com/)
  
2. Create a `flask-app` repository using [this guide](https://docs.docker.com/docker-hub/repos/create/#create-a-repository)

## 3 - Push Image to DockerHub
[This documentation](https://docs.docker.com/docker-hub/repos/create/#push-a-docker-container-image-to-docker-hub) walks through the process

### 3.1 - Login to DockerHub
Login to Docker Hub on the docker cli. Run the commansd below to login to docker

  - `docker login` - then enter your username and password
  - Alternatively, pass the username and password in a single CLI command. This is useful for scripts and build tools

### 3.2 - Push image to the repository
Images need to have the repository URL prefixed before it can be pushed

1. Tag the `flask-repo` image with the repository information
- `IMAGE_NAME=<hub-user>/flask-repo:dev`
- `docker tag $IMAGE_NAME`

1. Push the image 

`docker push $IMAGE_NAME`

## 4 - Open AWS CloudShell and Pull Repository
- [Follow insructions here](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html#how-to-get-started) to open a CloudShell
- Run commands below to clone the repositor and chnage to the directory for the lab
  ```
  git clone https://github.com/kordaralabs/free-containers-workshop.git
  cd free-containers-workshop/2-orchestrating-containers-with-ecs
  ```

## 5 - Setup Dependencies for ECS
### 5.1 - Create ECS Task Execution Role
Task Exectuion role allows ECS to make AWS API calls needed to setup the tasks. See more about [it here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html). 

- Create the role
```
aws iam create-role \
--role-name ecsTaskExecutionRole \
--assume-role-policy-document file://ecs-tasks-trust-policy.json
```

- Attach relevant permissions to the role 
```
aws iam attach-role-policy \
--role-name ecsTaskExecutionRole \
--policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### 5.2 - Create ECS Task Definition
Task Definition is a template for ECS to run tasks with. The task execution role created in section `5.1` is referenced in the `JSON` file. Ensure that the ARN is correct.

`aws ecs register-task-definition --cli-input-json file://task-definition.json`

### 5.3 - Grab Subnet IDs to use

- List all VPCs in the region
`aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock,IsDefault]' --output table`

- Set VPC_ID variable so it can be used later
`VPC_ID=<VPC ID>`

- Grab Subnet IDs using the VPC ID as a filter
```
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
--query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone,VpcId]' --output table
```

- Set Subnet ID Variables from output of previous command for future use
`SUBNET_1=<Subnet ID>`
`SUBNET_2=<Another Subnet ID>`

### 5.4 - Setup Security Groups

- Create a new Security Group for use with ECS and Load Balancers, then store the in SG_ID for future use
```
SG_ID=$(aws ec2 create-security-group --group-name allow-http \
--description "Allow HTTP port 80" --vpc-id $VPC_ID \
--query 'GroupId' --output text) && echo $SG_ID
```

- Allow HTTP Port 80 on the Security Group
`aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0`

## 6 - Create Standalone Task and test it
- Create a standalone ECS Task using the command below

```
TASK_ARN=$(aws ecs run-task --cluster default --task-definition flask-app:1 \
--awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_1],securityGroups=[$SG_ID],assignPublicIp=ENABLED} \
--query 'tasks[0].taskArn' --output text) && echo $TASK_ARN
```

- Test the task in a browser by visiting its public IP
```
aws ecs describe-tasks --cluster default --tasks $TASK_ARN \
--query 'tasks[0].attachments[0].details[?name==`publicIPv4Address`].value' --output text 
```

- Delete the Standalone ECS Task
`aws ecs stop-task --cluster default --task $TASK_ID`

## 7 - Create Highly Available Service
### 7.1 - Setup an Application Load Balancer
Steps to create an Application Load Balancer [with the CLI](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/tutorial-application-load-balancer-cli.html#create-load-balancer-aws-cli)

- Create a Target Group and store the ARN in `TG_ARN`
```
TG_ARN=$(aws elbv2 create-target-group --name flask-app-TG \
--protocol HTTP --port 80 --vpc-id $VPC_ID \
--query 'TargetGroups[0].TargetGroupArn' --output text) && echo $TG_ARN
```

- Create an Application Load Balancer and store the ARN in `LB_ARN`
```
LB_ARN=$(aws elbv2 create-load-balancer --name flask-app-LB \
--subnets $SUBNET_1 $SUBNET_1 --security-groups $SG_ID \
--query 'LoadBalancers[0].LoadBalancerArn' --output text) && echo $LB_ARN
```

- Create a Listener for port 80 and let it forward to the Target Group, then store the Listener ARN in `LST_ARN`
```
LST_ARN=$(aws elbv2 create-listener --protocol HTTP --port 80 \
--load-balancer-arn $LB_ARN --default-actions Type=forward,TargetGroupArn=$TG_ARN \
--query 'Listeners[0].ListenerArn' --output text) && echo $LST_ARN
```
### 6.2 - Create ECS Service
- Create ECS Service using previously created Load Balancer

```
aws ecs create-service --service-name flask-app-service --cluster default \
--task-definition my-task-definition \
--load-balancers targetGroupArn=$TG_ARN,containerName="flask-app",containerPort=80
```

- Test the highly available application by visiting the Load Balancer URL in a browser
`aws elbv2 describe-load-balancers --load-balancer-arns $LB_ARN --query 'LoadBalancers[0].DNSName' --output text`

## 7 - Cleanup
- Delete the Load Balancer
`aws elbv2 delete-load-balancer --load-balancer-arn $LB_ARN`

- Delete the Load Balancer Target Group
`aws elbv2 delete-target-group --target-group-arn $TG_ARN`

- Delete Load Balancer Listener
`aws elbv2 delete-listener --listener-arn $LST_ARN`

- Delete the ECS Service. `--force` allows deleting a service without scaling the tasks to 0
`aws ecs delete-service --cluster default --service flask-app-service --force`

- Deregister and delete each Task Definition revision
  - List all revisions
  `aws ecs list-task-definition-families --family-prefix flask-app --query 'families[].revision' --output table`

  - Deregister each revision number, replace `<revision number>` with the Task Definition revision number
  `aws ecs deregister-task-definition --task-definition flask-app:<revision number>`

  - Delete the Task Defintion revision, replace `<revision number>` with the Task Definition revision number
  `aws ecs delete-task-definitions --task-definition flask-app:<revision number>`

- Delete the Security Group
`aws ec2 delete-security-group --group-id $SG_ID`

- Delete ECS Task Execution Role
`aws iam `
  
