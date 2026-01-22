# Airflow 3.x Local Development Environment

A complete Docker-based development environment for Apache Airflow 3.x with PostgreSQL and Redis, designed to work on both macOS and Linux.

## Features

- **Airflow 3.1.6**: Latest stable version of Apache Airflow 3.x
- **Celery Executor**: Distributed task execution with Redis as message broker
- **PostgreSQL Database**: Robust metadata storage
- **Cross-platform**: Works on both macOS (Intel/Apple Silicon) and Linux
- **Hot-reload**: DAGs are automatically picked up from the local `dags/` directory
- **Persistent Storage**: Database and logs persist between container restarts

## Prerequisites

- Docker and Docker Compose (or Docker Desktop)
- At least 4GB of available RAM
- At least 2GB of available disk space

### System Requirements

**macOS:**
- Docker Desktop 4.0+
- macOS 10.15+ (Catalina or later)

**Linux:**
- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Clone or download this repository**

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` if you need to customize any settings.

3. **Start the services:**
   ```bash
   docker compose up -d
   ```

4. **Access Airflow Web UI:**
   Open http://localhost:8080 in your browser

5. **Default credentials:**
   - Username: `admin`
   - Password: `admin`

## Project Structure

```
.
├── dags/                 # Your DAG files go here
│   └── example_dag.py   # Sample DAG to test the setup
├── logs/                 # Airflow logs (auto-generated)
├── plugins/              # Custom plugins (optional)
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Custom Airflow image
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── env.example          # Environment variables template
└── README.md           # This file
```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and modify as needed:

```bash
# Airflow Core Settings
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=false

# Database Connection
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# Celery Configuration
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow

# API Server Settings
AIRFLOW__API__EXPOSE_CONFIG=true
```

### Customizing Resources

If you need more resources or different configurations, edit `docker-compose.yml`:

```yaml
services:
  airflow-worker:
    environment:
      AIRFLOW__CELERY__WORKER_CONCURRENCY: 4  # Increase worker concurrency
    deploy:
      resources:
        limits:
          memory: 2G
```

## Usage

### Adding DAGs

1. Place your DAG Python files in the `dags/` directory
2. Airflow will automatically detect and load them
3. Access them through the web UI at http://localhost:8080

### Managing Services

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f airflow-apiserver
docker compose logs -f airflow-scheduler
docker compose logs -f airflow-worker

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes database data)
docker compose down -v

# Rebuild the Airflow image (after changing requirements.txt)
docker compose build --no-cache airflow-apiserver
```

### Database Management

The PostgreSQL database persists data between container restarts. To reset:

```bash
# Stop services and remove database volume
docker compose down -v

# Restart (this will recreate the database)
docker compose up -d
```

### Troubleshooting

#### Common Issues

**Port conflicts:**
- The default configuration uses ports 5434 (PostgreSQL) and 6380 (Redis) to avoid conflicts
- If these ports are still in use, change the port mappings in `docker-compose.yml`:
  ```yaml
  postgres:
    ports:
      - "5435:5432"  # Use different host port
  redis:
    ports:
      - "6381:6379"  # Use different host port
  ```

**Permission issues on Linux:**
- Ensure your user is in the `docker` group:
  ```bash
  sudo usermod -aG docker $USER
  # Log out and back in for changes to take effect
  ```

**Memory issues:**
- Airflow with all services requires ~2-4GB RAM
- Increase Docker Desktop memory allocation if needed

#### Logs and Debugging

```bash
# View all service logs
docker compose logs

# View specific service logs
docker compose logs airflow-scheduler

# View logs in real-time
docker compose logs -f

# Access container shell for debugging
docker compose exec airflow-apiserver bash
```

### Development Workflow

1. **Edit DAGs locally** in the `dags/` directory
2. **Test DAGs** through the Airflow web UI
3. **Monitor execution** via logs and task instances
4. **Scale workers** by adjusting `docker-compose.yml` or running multiple worker instances

### Adding Dependencies

To add Python packages to your Airflow environment:

1. Edit `requirements.txt`
2. Rebuild the image:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

## Services Overview

- **airflow-apiserver**: API server and Web UI on port 8080 (replaces webserver in Airflow 3.x)
- **airflow-scheduler**: Schedules and triggers DAG runs
- **airflow-worker**: Executes tasks (Celery workers)
- **airflow-triggerer**: Handles deferrable task triggers
- **postgres**: Metadata database (port 5434 on host)
- **redis**: Message broker for Celery (port 6380 on host)

## Authentication

This setup uses **FAB (Flask-AppBuilder) Auth Manager** by default, which provides a traditional username/password login system.

### Default Credentials

- **URL:** http://localhost:8080
- **Username:** `admin`
- **Password:** `admin`

### Changing Username and Password

To change the default credentials, edit the `airflow-init` service in `docker-compose.yml`:

```yaml
airflow-init:
  environment:
    _AIRFLOW_WWW_USER_USERNAME: your_username
    _AIRFLOW_WWW_USER_PASSWORD: your_password
```

Then reset and restart to apply changes:

```bash
# Remove existing database (required to recreate user)
docker compose down -v

# Start fresh
docker compose up -d
```

### Switching to SimpleAuthManager

Airflow 3.x introduced a new **SimpleAuthManager** as an alternative to FAB. To switch:

1. Edit `docker-compose.yml` and change the `x-airflow-common` environment section:

```yaml
x-airflow-common: &airflow-common
  environment:
    # Comment out FAB Auth Manager
    # AIRFLOW__CORE__AUTH_MANAGER: airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
    # AIRFLOW__API__AUTH_BACKENDS: airflow.providers.fab.auth_manager.api.auth.backend.basic_auth,airflow.providers.fab.auth_manager.api.auth.backend.session

    # Use SimpleAuthManager instead
    AIRFLOW__CORE__AUTH_MANAGER: airflow.api_fastapi.auth.managers.simple.simple_auth_manager.SimpleAuthManager
```

2. Also update the `airflow-init` service environment (remove or comment out the FAB-specific settings):

```yaml
airflow-init:
  environment:
    # Remove these lines when using SimpleAuthManager:
    # AIRFLOW__CORE__AUTH_MANAGER: airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
    # _AIRFLOW_WWW_USER_CREATE: "true"
    # _AIRFLOW_WWW_USER_USERNAME: admin
    # _AIRFLOW_WWW_USER_PASSWORD: admin
```

3. Restart with a fresh database:

```bash
docker compose down -v
docker compose up -d
```

4. **Important:** SimpleAuthManager generates a random password at startup. Check the logs for the password:

```bash
docker compose logs airflow-apiserver | grep "Password for user"
```

Output will show something like:
```
Simple auth manager | Password for user 'admin': <random-password>
```

### Auth Manager Comparison

| Feature | FAB Auth Manager | SimpleAuthManager |
|---------|------------------|-------------------|
| Password | User-defined | Auto-generated at startup |
| User management | Full RBAC support | Basic single-user |
| Configuration | More options | Minimal setup |
| Recommended for | Production-like setups | Quick testing |

## Security Notes

- Default credentials are `admin`/`admin` - change in production
- This setup is for local development only
- Do not expose port 8080 to the internet without proper authentication
- Consider using Airflow's RBAC features for multi-user setups

## Upgrading Airflow

To upgrade to a newer version of Airflow 3.x:

1. Update the version in `Dockerfile`:
   ```dockerfile
   FROM apache/airflow:3.x.x-python3.12
   ```

2. Check for breaking changes in the [Airflow release notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html)

3. Rebuild and restart:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

## Contributing

1. Test your changes locally
2. Ensure cross-platform compatibility
3. Update documentation as needed

## License

This project is provided as-is for educational and development purposes.