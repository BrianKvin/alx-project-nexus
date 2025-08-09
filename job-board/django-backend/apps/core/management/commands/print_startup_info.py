from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Print helpful startup URLs for the developer environment"

    def handle(self, *args, **options):
        # ANSI colors
        BOLD = "\033[1m"
        GREEN = "\033[0;32m"
        BLUE = "\033[0;34m"
        NC = "\033[0m"  # No Color

        # Base application URL (inside or outside Docker)
        base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

        # Feature toggles (optional)
        swagger_enabled = os.getenv("SWAGGER_ENABLED", "false").lower() == "true"
        graphql_enabled = os.getenv("GRAPHQL_ENABLED", "false").lower() == "true"

        # External service ports (with sensible defaults for dev/docker)
        mailhog_port = os.getenv("MAILHOG_PORT", "8025")
        flower_port = os.getenv("FLOWER_PORT", "5555")
        minio_console_port = os.getenv("MINIO_CONSOLE_PORT", "9001")
        minio_api_port = os.getenv("MINIO_API_PORT", "9000")
        es_port = os.getenv("ELASTICSEARCH_PORT", "9200")

        # Construct URLs
        urls = [
            ("API Root", f"{base_url}/"),
            ("Django Admin", f"{base_url}/admin/"),
            ("Health", f"{base_url}/health/"),
        ]

        if swagger_enabled:
            swagger_path = os.getenv("SWAGGER_PATH", "/api/docs/")
            urls.append(("API Docs (Swagger)", f"{base_url}{swagger_path}"))

        if graphql_enabled:
            graphql_path = os.getenv("GRAPHQL_PATH", "/graphql/")
            urls.append(("GraphQL Playground", f"{base_url}{graphql_path}"))

        # Common dev services (available when using docker-compose)
        urls.extend([
            ("MailHog (Emails)", f"http://localhost:{mailhog_port}"),
            ("Flower (Celery)", f"http://localhost:{flower_port}"),
            ("MinIO Console", f"http://localhost:{minio_console_port}"),
            ("MinIO S3 Endpoint", f"http://localhost:{minio_api_port}"),
            ("Elasticsearch", f"http://localhost:{es_port}"),
        ])

        # Print banner
        self.stdout.write("")
        self.stdout.write(f"{GREEN}{BOLD}Project is running!{NC}")
        self.stdout.write(f"{BOLD}Useful URLs:{NC}")

        for label, url in urls:
            self.stdout.write(f"- {label}: {BLUE}{url}{NC}")

        self.stdout.write("")
        return None
