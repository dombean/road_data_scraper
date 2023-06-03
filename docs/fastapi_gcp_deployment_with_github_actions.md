# FastAPI Deployment with Google Cloud Run using GitHub Actions

This repository includes a GitHub Action that will automatically build and deploy your FastAPI application to Google Cloud Run upon execution.

## GitHub Action

The GitHub Action workflow is defined in `.github/workflows/build_and_deploy.yml`.

The workflow is triggered manually with `workflow_dispatch`.

It includes the following jobs:
1. **Checkout repository**: This checks out your repository so the workflow can access it.
2. **Set up Docker**: Sets up Docker using the Docker GitHub Action.
3. **Set up GCP credentials** (Optional): This step creates a JSON file with your Google Cloud Platform (GCP) credentials stored in a GitHub secret named `GCP_CREDS`. This step is optional and may not be necessary for all applications. In the case of our FastAPI app, we require this JSON file for operation.
4. **Authenticate with GCP**: This step uses the Google GitHub Action to authenticate with GCP directly using the `GCP_CREDS` secret stored in your GitHub repository.
5. **Set GCP Project**: Configures the gcloud command-line tool with your GCP project ID.
6. **Modify Script**: This step replaces placeholders in the `docker-build-and-deploy.sh` script with your actual values and makes the script executable.
7. **Build and Deploy**: Executes the `docker-build-and-deploy.sh` script to build and deploy your FastAPI app.

## Bash Script: docker-build-and-deploy.sh

The `docker-build-and-deploy.sh` script is the backbone of this workflow. It builds a Docker image for the FastAPI application, pushes the image to the Google Container Registry (GCR), and deploys the image to Google Cloud Run.

Usage: `./docker-build-and-deploy.sh <build-type> <cache-option>`

Here `<build-type>` can be either 'local' or 'cloud', and `<cache-option>` is optional and can be either 'cache' or 'no-cache' (only applicable for local builds).

## Setup

To use this workflow, you will need to replace all placeholders in both the GitHub workflow and bash script with your own values.

Placeholders to replace:

- `your-image-name`: The name you wish to give to your Docker image.
- `your-project-id`: The ID of your GCP project.
- `your-service-name`: The name you wish to give to your Cloud Run service.
- `region`: The region where your Cloud Run service should be deployed.

Furthermore, make sure to provide your GCP credentials as a secret in your GitHub repository. Name the secret `GCP_CREDS`.

## Requirements

Before using this workflow, ensure you have the following:

- A FastAPI application that you wish to deploy.
- Docker installed, as it is required for building the Docker image.
- A Google Cloud Platform account and a project on it.
- gcloud command-line tool installed and authenticated with your GCP account.
- GitHub repository where the FastAPI application lives.
- GCP credentials saved as a GitHub secret.
- Permissions to execute the `docker-build-and-deploy.sh` script.

## Triggering the Workflow

This workflow can be triggered manually. To do this, navigate to the **"Actions"** tab of your GitHub repository, select the workflow, and click on **"Run workflow"**.

## Viewing your Deployed Application

After the workflow completes, you can find the URL of your deployed FastAPI application by running the following command in your local terminal (replace `your-service-name` and `region` with your actual values):

```
gcloud run services describe your-service-name --region=region --format="value(status.url)"
```

Alternatively, you can also find the URL in the "Cloud Run" section of the Google Cloud Console.

## Troubleshooting

If you run into any issues while setting up or executing this workflow, consider the following tips:

- Make sure all placeholders in the GitHub workflow and bash script have been replaced with your values.
- Verify that the GCP credentials saved in your GitHub secrets are correct.
- Ensure that you have permissions to deploy applications in the GCP project.
- If the workflow is failing on the `Build and Deploy` step, make sure the `docker-build-and-deploy.sh` script is executable. You can make a file executable by running `chmod +x your-file-name` in your terminal.
- For detailed error messages, you can check the "Actions" tab in your GitHub repository.
