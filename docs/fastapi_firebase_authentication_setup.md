# Firebase Authentication with FastAPI

This technical documentation provides step-by-step instructions on how to integrate Firebase Authentication, a secure and easy-to-use authentication service, with FastAPI, a modern web framework for building APIs with Python.

## Prerequisites

Before setting up Firebase Authentication with FastAPI, make sure you have the following prerequisites:

- A Firebase project created on the Firebase Console. If you don't have a Firebase project, you can create one by following the instructions at the Firebase Console.
- The Firebase CLI installed on your local development machine. You can install it by following the instructions in the Firebase CLI documentation.
- Python 3.x installed on your local development machine. You can download and install Python from the official Python website: Python.org.
- The firebase-admin Python library installed. You can install it using pip by running the following command:

```python
pip install firebase-admin
```

- The google-cloud-secret-manager Python library installed. You can install it using pip by running the following command:

```python
pip install google-cloud-secret-manager
```

- The python-dotenv Python library installed. You can install it using pip by running the following command:

```python
pip install python-dotenv
```

## Local Development Setup

For local development, you will need to create a `.env` file in your project root directory to hold your environment variables. Specifically, you need to set the `GOOGLE_APPLICATION_CREDENTIALS` variable to point to your service account key JSON file.

Your `.env` file should look something like this:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/serviceAccountKey.json
```

Replace `/path/to/your/serviceAccountKey.json` with the actual path to your JSON file.

When you start the application locally, it will use the credentials specified in this file to authenticate with Firebase.

To protect your sensitive data, ensure that the `.env` file is included in your `.gitignore` file to prevent it from being tracked by version control. In addition, add `.env` to your `.dockerignore` file to prevent it from being included in your Docker image, which could potentially expose your sensitive data.

## Step 1: Set up Firebase Authentication

Go to the Firebase Console and select your Firebase project.

In the left sidebar, click on "Authentication".

In the "Authentication" section, click on the "Sign-in method" tab.

Enable the desired sign-in methods, such as Email/Password, Google, or others, depending on your application's requirements.

Configure the sign-in methods according to your preferences, such as allowing user registration, setting password complexity requirements, etc.

## Step 2: Add Firebase Service Account JSON and API Key to Google Secret Manager

First, go to the Firebase Console and generate a new private key for your Firebase project. Then, add the Firebase JSON file and API Key to Google Secret Manager in your Google Cloud Platform project.

Make sure you take note of the secret IDs for both the Firebase JSON and API Key as they will be required in the code later.

## Step 3: Configure FastAPI for Firebase Authentication

Create a new FastAPI project or open an existing FastAPI project in your preferred code editor.

In the main file of your FastAPI application, add the following code to initialize Firebase with your service account:

```python
import json
import os

import google.auth
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app
from google.cloud import secretmanager

# Load environment variables from .env file
load_dotenv()

# Obtain the value of GOOGLE_APPLICATION_CREDENTIALS from the environment
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Check if GOOGLE_APPLICATION_CREDENTIALS is set
if credentials_path:
    # Use the specified service account key file
    google_credentials = credentials_path
else:
    # Use default application credentials
    google_credentials, _ = google.auth.default()


def access_secret_version(project_id: str, secret_id: str, version_id: str) -> str:
    """
    Accesses the payload of the specified version of a secret stored in Google Secret Manager.

    Retrieves the secret payload by providing the Google Cloud project ID, secret ID,
    and version ID. The function uses the Secret Manager client to access the secret
    version and returns the decrypted payload as a string.

    Args:
        project_id (str): The Google Cloud project ID where the secret is located.
            Example: 'my-project'.
        secret_id (str): The ID of the secret to access.
        version_id (str): The version ID of the secret to access.
            Example: 'latest'.

    Returns:
        str: The decrypted payload of the secret version.

    Raises:
        google.api_core.exceptions.NotFound: If the specified project, secret, or version
            is not found in Google Secret Manager.
        google.api_core.exceptions.PermissionDenied: If the caller does not have the necessary
            permissions to access the secret version.
    """
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=secret_name)
    payload = response.payload.data.decode("UTF-8")
    return payload


PROJECT_ID = "your-google-cloud-project-id"

# Get Firebase credentials from Secret Manager
firebase_credentials_json = access_secret_version(
    project_id=PROJECT_ID, secret_id="your-firebase-json-secret-id", version_id="latest"
)
firebase_credentials_dict = json.loads(firebase_credentials_json)

firebase_api = access_secret_version(
    project_id=PROJECT_ID, secret_id="your-firebase-api-key-secret-id", version_id="latest"
)

# Initialize Firebase app
cred = credentials.Certificate(firebase_credentials_dict)
default_app = initialize_app(cred)
```

Replace 'your-google-cloud-project-id', 'your-firebase-json-secret-id', and 'your-firebase-api-key-secret-id' with your actual Google Cloud project ID and the secret IDs for your Firebase JSON and API Key.

This script initializes Firebase in your FastAPI application using the Firebase JSON and API Key stored in Google Secret Manager. It uses the Google Cloud Secret Manager client to access the secrets and Firebase Admin SDK to initialize Firebase.

With this setup, your FastAPI application can now use Firebase Authentication to authenticate users.

## How Firebase Authentication Works with FastAPI

FastAPI is a modern web framework that makes it easy to build APIs. Firebase Authentication provides a secure and easy-to-use service for authenticating these API requests.

When a user logs into your application, Firebase Authentication will return a token. This token can then be included in the HTTP Authorization header for API requests to your FastAPI application.

Your FastAPI application can verify the token using the Firebase Admin SDK. If the token is valid, the request is authenticated. Otherwise, the request is rejected.

This setup provides a secure and scalable solution for authenticating API requests in your FastAPI application.

## Conclusion

Congratulations! You have successfully set up Firebase Authentication with FastAPI. Now, your FastAPI application can leverage the powerful authentication features provided by Firebase Authentication to secure your API endpoints and authenticate your users.

With Firebase Authentication, you can easily integrate various sign-in methods, such as email/password, Google, Facebook, and more, to provide a seamless authentication experience for your users.

Feel free to explore the Firebase Authentication documentation and the FastAPI documentation for more advanced authentication features and customization options to suit your application's specific needs.
