#!/bin/bash

# Description: This script builds and deploys a Docker image to Google Cloud Run.
# Usage: ./docker-build-and-deploy.sh <build-type> <cache-option>
#   - <build-type> can be either 'local' or 'cloud'.
#   - <cache-option> is optional and can be either 'cache' or 'no-cache' (only applicable for local builds).
# Example: ./docker-build-and-deploy.sh local cache
# Example: ./docker-build-and-deploy.sh local no-cache
# Example: ./docker-build-and-deploy.sh cloud

# Note: This script should be located in the same directory as the Dockerfile.

# Assign values to variables
image_name="your-image-name"
project_id="your-project-id"
service_name="your-service-name"
region="europe-west2"

# Function to display script usage
function display_usage() {
    echo "Usage: $0 <build-type> <cache-option>"
    echo "  - <build-type> can be either 'local' or 'cloud'."
    echo "  - <cache-option> is optional and can be either 'cache' or 'no-cache' (only applicable for local builds)."
    echo "Example: $0 local cache"
    echo "Example: $0 local no-cache"
    echo "Example: $0 cloud"
}

# Validate and process command line arguments
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    display_usage
    exit 1
fi

build_type=$1
cache_option=$2

if [ "$build_type" != "local" ] && [ "$build_type" != "cloud" ]; then
    echo "Invalid build type. Please specify either 'local' or 'cloud'."
    display_usage
    exit 1
fi

if [ "$build_type" == "local" ] && [ "$cache_option" != "cache" ] && [ "$cache_option" != "no-cache" ]; then
    echo "Invalid cache option. Please specify either 'cache' or 'no-cache' for local builds."
    display_usage
    exit 1
fi

# Check command line flag
if [ "$1" == "local" ]; then
    if [ "$2" == "cache" ]; then
        # Build the Docker image locally with cache
        docker build -t $image_name -f Dockerfile .

        # Tag and push the Docker image to GCR
        docker tag $image_name gcr.io/$project_id/$image_name
        docker push gcr.io/$project_id/$image_name
    elif [ "$2" == "no-cache" ]; then
        # Build the Docker image locally without cache
        docker build -t $image_name -f Dockerfile . --no-cache

        # Tag and push the Docker image to GCR
        docker tag $image_name gcr.io/$project_id/$image_name
        docker push gcr.io/$project_id/$image_name
    else
        echo "Invalid argument. Please specify either 'cache' or 'no-cache'."
        exit 1
    fi
elif [ "$1" == "cloud" ]; then
    # Build the Docker image using Google Cloud Build
    gcloud builds submit --tag gcr.io/$project_id/$image_name --project $project_id .
else
    echo "Invalid argument. Please specify either 'local' or 'cloud'."
    exit 1
fi

# Deploy the image to Cloud Run
gcloud run deploy $service_name \
    --image gcr.io/$project_id/$image_name \
    --platform managed \
    --region $region \
    --timeout "3600" \
    --cpu "4" \
    --memory "16Gi" \
    --min-instances "1" \
    --max-instances "10" \
    --concurrency "1" \
    --allow-unauthenticated

# View the URL of the deployed service
gcloud run services describe $service_name --region=$region --format="value(status.url)"
