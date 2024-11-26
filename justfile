# Use with https://github.com/casey/just
#
# Syntax used here:
# @ -> if a just script is prefixed with @, the script is not printed out when run
# _ -> private, ommited from 'just --list'
# recipe arguments will be passed as positional arguments to commands
#
# Formatting:
# run `just --fmt --unstable` to format this file
#
# use bash as default shell for recipes

set shell := ["bash", "-uc"]
set positional-arguments := true

# First recipe is default recipe executed with `just` command

# List available recipes
_list_all:
    @just --list --unsorted --justfile {{ justfile() }}

# Set user id and user group id into .env file for docker compose to pass down as build arguments
@_docker-build-args path=".env":
    if ! grep -q "^UID=" {{ path }} 2> /dev/null; then printf "\n%s\n" "UID=$(id -u)" >> {{ path }}; fi
    if ! grep -q "^GID=" {{ path }} 2> /dev/null; then printf "\n%s\n" "GID=$(id -g)" >> {{ path }}; fi

# Runs poetry inside the django container with any optional args
poetry *args: (up "django -d")
    docker compose exec django bash -ic "poetry {{ args }}"


# Runs the manage.py inside the django container with optional args
@manage *args: (up "django -d")
    docker compose exec django bash -ic "/development/app/manage.py {{ args }}"

# Start a lightweight development Django web server
run *args:
    just manage runserver 0.0.0.0:8000 {{ args }}

# Start interactive Python shell with autoloading of the apps database models and subclasses of user-defined classes
shell_plus *args:
    just manage shell_plus {{ args }}

# Runs the docker compose exec django bash with optional args
bash *args: (up "django -d")
    docker compose exec django bash {{ args }}

# Build and run the test docker compose file
test *args: _docker-build-args
    docker compose -f docker-compose.test.yml run django {{ args }}

# "Runs migrate via manage and manage.py inside the django container with optional args"
migrate *args:
    just manage migrate {{ args }}

# "Runs make-migrations via manage and manage.py inside the django container with optional args"
make-migrations *args:
    just manage make-migrations {{ args }}

# ~~~~ Docker management ~~~~ #

# Docker compose up - starts, and attaches to containers for a service
up *args: _docker-build-args
    docker compose up {{ args }}

# Docker compose down - stops, and detaches containers for a service
down *args: _docker-build-args
    docker compose down --remove-orphans {{ args }}

# Build the docker container images before starting the containers
build *args: _docker-build-args
    echo "Building the docker container images..."
    docker compose --progress=plain build --pull --no-cache {{ args }}
