# GCP Project Setup with Terraform

This repository contains Terraform scripts to set up a Google Cloud Platform (GCP) project, enable APIs, create a service account, and configure a Cloud Storage bucket.

## Prerequisites

Before you begin, make sure you have the following:

- [Terraform](https://www.terraform.io/downloads.html) installed on your machine.
- A Google Cloud Platform (GCP) account.
- Project Owner or Editor permissions for the GCP project you want to configure.

## Getting Started

Follow the steps below to set up your GCP project using Terraform:

1. Clone this repository to your local machine.

```shell
git clone <repository_url>
cd <repository_directory>
```

2. Open the `terraform.tfvars` file and provide values for the required variables. This file contains the configuration values for your project, such as the `project_id`.

```shell
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars
```

3. Initialize the Terraform working directory.

```shell
terraform init
```

4. Review the execution plan.

```shell
terraform plan
```

This command will show you the resources that Terraform plans to create or modify in your GCP project. Review the plan carefully to ensure it matches your expectations.

5. Apply the Terraform configuration to create the resources.

```shell
terraform apply
```

Enter `yes` when prompted to confirm the resource creation. Terraform will create the necessary resources in your GCP project.

6. Once the Terraform apply completes successfully, the GCP project setup is complete.

## Additional Configuration

### Customize Region

By default, the region is set to __"europe-west2"__ in the Terraform script. If you want to configure a different region, update the `bucket_location` variable in `terraform.tfvars` file.

### Service Account Key

After running `terraform apply`, a service account will be created as specified in the Terraform script. To generate and download the corresponding service account key, you will need to manually perform the following steps:

1. Navigate to the [Google Cloud Console IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts).
2. Select your project.
3. Find the service account that was created by Terraform. It should be listed in the table of service accounts.
4. Click on the three-dot icon on the right side of the service account row, then select `Manage keys`.
5. In the `Keys` section, click on `ADD KEY`, then select `Create new key`.
6. In the `Create private key` section, select `JSON` as the key type.
7. Click `CREATE`. The key will be automatically downloaded as a JSON file.

This JSON key file can be used to authenticate your applications or services with Google Cloud Platform (GCP) APIs. Please remember to store this key securely, as it can provide full access to your GCP resources.

## Cleaning Up

To clean up and delete the resources created by Terraform, run:

```shell
terraform destroy
```

Enter `yes` when prompted to confirm the resource deletion.

