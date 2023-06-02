# Introduction

This README is intended as a comprehensive guide to setting up your Google Cloud Project (GCP), managing Docker images, deploying these images using Google Cloud Run, and connecting your Cloud Run service with Google Secrets. These instructions are designed to be easy to follow, regardless of your level of experience with Google Cloud or Docker. However, it's important to note that this guide assumes that Docker and Google Cloud SDK (`gcloud`) are installed and authenticated correctly with the appropriate project.

# Google Project Setup

Setting up your Google Cloud Project (GCP) correctly is an essential first step in this process. This includes setting your active account, choosing your active project, and verifying the service name and service account permissions. An incorrectly set up GCP can lead to a range of issues, the most common being the __"PERMISSION_DENIED"__ error. 

If you're still encountering the __"PERMISSION_DENIED"__ error after ensuring that the appropriate roles have been granted to your account, there might be a couple of other factors at play. Here are a few troubleshooting steps you can try:

1. Verify the active account: Confirm that you're using the correct Google Cloud account by running the following command in your terminal:

   ```bash
   gcloud auth list
   ```

   Ensure that the account listed is the one with the necessary permissions.

2. Verify the active project: Double-check that you have set the correct project as the active project by running the following command:

   ```bash
   gcloud config get-value project
   ```

   If it's not the correct project, set the correct one using:

   ```bash
   gcloud config set project <your-project-id>
   ```

3. Confirm the service name: Make sure that the service name you're deploying (`ons-fi-road-sensors-docker`) matches the actual Cloud Run service name you're trying to deploy. You can verify the service name by checking your Cloud Run services in the Cloud Console.

4. Check service account permissions: Ensure that the service account associated with your project has the necessary permissions. You can find the service account email address by running:

   ```bash
   gcloud iam service-accounts list
   ```

   Grant the `Service Account User` role (`roles/iam.serviceAccountUser`) to the service account if it doesn't have it already:

   ```bash
   gcloud projects add-iam-policy-binding <your-project-id> --member="serviceAccount:<service-account-email>" --role="roles/iam.serviceAccountUser"
   ```

If you have followed these steps and are still experiencing issues, it's possible that there might be additional configuration or permission settings specific to your environment. In such cases, it may be helpful to consult with your Google Cloud administrator or review the Cloud Run documentation for further troubleshooting guidance.

The subsequent sections of this guide, "Docker Build and Run," "Deploying your Docker Container to Cloud Run," and "Connect Google Cloud Run with Google Secrets," will further help you streamline your project setup by outlining the necessary steps for building and deploying your Docker images and connecting your service to Google Secrets.

# Docker Build and Run

Docker enables you to package your application into a standardized unit for software development, known as a Docker image. In this section, we'll walk you through the steps for building and running your Docker image.

To construct your Docker image, navigate to the directory containing your Dockerfile. Then, execute the following commands:

## Local Build, Run and Push

```bash
# This command builds your Docker image using the Dockerfile located in the current directory
docker build -t <image-name> -f Dockerfile .

# If you want to construct your image without utilizing any cached layers
docker build -t <image-name> -f Dockerfile . --no-cache
```

### Run

Once your Docker image is built, you're ready to run it locally. Here's how:

```bash
# This command launches your Docker image in a new container, linking port 80 of the container to port 80 on your host machine
docker run -it --env PORT=80 -p 80:80 <image-name>

# If you desire to initiate an interactive shell in a new container (useful for debugging)
docker run -it --env PORT=80 -p 80:80 <image-name> sh
```

Ensure you replace `<image-name>` in the commands with the name you've designated to your Docker image.

### Push

After you've built your Docker image locally, the next step is to push it to the Google Container Registry (GCR). This involves tagging the image with the registry's URL and then using the `docker push` command:

```bash
docker tag <image-name> eu.gcr.io/<project-id>/<image-name>
docker push eu.gcr.io/<project-id>/<image-name>
```

Replace `<image-name>` with the name of your Docker image and `<project-id>` with your Google Cloud project ID.

## Google Cloud Build

You may prefer to use Google Cloud Build to build your Docker images. This is especially useful if you have a complex build process or you want to automate your builds. Google Cloud Build allows you to define and manage your builds using a YAML configuration file.

To build a Docker image using Google Cloud Build, you can use the following command:

```bash
gcloud builds submit --tag gcr.io/$project_id/$image_name --project $project_id .
```

Replace `<project-id>` with your Google Cloud project ID and `<image-name>` with the name of your Docker image.

Make sure you have the Google Cloud SDK (`gcloud`) installed and authenticated with the correct project before running these commands.

Please note that using Google Cloud Build may incur costs. Check the [Google Cloud Build pricing](https://cloud.google.com/build/pricing) page for more information.

## Deploy

Once your Docker image has been pushed to GCR, you're now ready to deploy it to Google Cloud Run. Use the gcloud run deploy command to create a new service or revise an existing one:

```bash
gcloud run deploy <service-name> \
  --image eu.gcr.io/<project-id>/<image-name> \
  --platform managed \
  --region europe-west2 \
  --timeout "3600" \
  --cpu "4" \
  --memory "16Gi" \
  --min-instances "1" \
  --max-instances "10" \
  --concurrency "1"
```
Replace the following placeholders in the command:

- `<service-name>`: Name of your Cloud Run service.
- `<image-name>`: Name of your Docker image.
- `<project-id>`: Your Google Cloud project ID.

Before running these commands, ensure that you have Docker and the Google Cloud SDK (`gcloud`) installed and authenticated with the correct project. Each of these commands lets you configure your service's specifications, such as CPU allocation, memory allocation, region, timeout, and instance count. You may adjust these as necessary based on the requirements of your project.

## View Deployed Service

After successfully deploying the service, you may want to view the deployed application. The gcloud run services describe command can be used to get the URL of the deployed service:

```bash
gcloud run services describe <service-name> --region=<region> --format="value(status.url)"
```

## Updating the Service

In case you make changes to your application, you would need to rebuild your Docker image and re-deploy it. This can be achieved by repeating the build, push and deploy steps described earlier.

# Connect Google Cloud Run with Google Secrets

Working with Google Cloud Run involves handling sensitive data like credentials and API keys, which need to be stored securely. Google Secret Manager is a tool that provides secure and convenient storage for such sensitive data.

In order for Cloud Run to access these secrets, the necessary permissions need to be granted to the Cloud Run service account. By default, Cloud Run uses a service account with the following format: `<project-number>-compute@developer.gserviceaccount.com`.

To set up this access, please follow these steps:

1. Open the Google Cloud Console at [https://console.cloud.google.com/](https://console.cloud.google.com/).

2. Select your project from the project dropdown menu in the navigation bar.

3. Click on the navigation menu (three horizontal lines in the upper left corner), and navigate to "IAM & Admin" > "IAM".

4. In the list of accounts, locate the service account that corresponds to your Cloud Run service. You can do this by entering `<project-number>-compute@developer.gserviceaccount.com` in the search bar, replacing `<project-number>` with your actual project number.

5. Once you have found the service account, click on the pencil icon next to it to edit its permissions.

6. Click on the "Add another role" button.

7. In the "Select a role" dropdown, search for __"Secret Manager Secret Accessor"__ and select it.

8. Click on the "Save" button to apply the changes and grant the role.

After the __"Secret Manager Secret Accessor"__ role is granted to the Cloud Run service account, it will have the necessary permissions to access secrets stored in Google Secret Manager. 

Please note: It can take a few minutes for the permission changes to propagate. If you encounter an error after granting the permission, please wait a few minutes before trying again.
