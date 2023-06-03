variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "your-project-id"
}
variable "bucket_name" {
  description = "Name of the Cloud Storage bucket"
  type        = string
  default     = "my-bucket"
}

variable "bucket_location" {
  description = "Location of the Cloud Storage bucket"
  type        = string
  default     = "eu"
}

resource "random_id" "random_suffix" {
  byte_length = 4
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-west-2"
}

# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Create the service account
resource "google_service_account" "my_service_account" {
  account_id   = "my-service-account"
  display_name = "My Service Account"
}

# Assign the required roles to the service account
resource "google_project_iam_member" "storage_admin_role" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_project_iam_member" "service_account_user_role" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_project_iam_member" "cloud_build_builder_role" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_project_iam_member" "container_registry_service_agent_role" {
  project = var.project_id
  role    = "roles/containerregistry.ServiceAgent"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_project_iam_member" "cloud_run_admin_role" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_project_iam_member" "secret_manager_admin_role" {
  project = var.project_id
  role    = "roles/secretmanager.admin"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

# Enable APIs
resource "google_project_service" "cloud_build" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"
}

resource "google_project_service" "container_registry" {
  project = var.project_id
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "secrets_manager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
}

resource "google_project_service" "cloud_storage" {
  project = var.project_id
  service = "storage.googleapis.com"
}

# Create a Cloud Storage Bucket
resource "google_storage_bucket" "my_bucket" {
  name     = "${var.bucket_name}-${random_id.random_suffix.hex}"
  location = var.bucket_location
}
