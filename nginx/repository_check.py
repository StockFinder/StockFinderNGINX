import re
from asyncio.log import logger

import docker
from git import Repo

PATH_OF_GIT_REPO = "/opt/docker/StockFinderModules/ImagesWebServer/NGINX/nginx/static/uuid_products"


def get_stockfinder_container(running_container):
    desired_container = None
    for container in running_container:
        if container.name != "stockfinder_images":
            continue
        desired_container = container
        break
    return desired_container


def main():

    ## GIT
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.fetch()
        status = repo.git.status()
        result = re.findall("Your branch is behind", status)
        if not result:
            logger.warning("No hay nuevos commits")
            return True

        logger.warning("Sí hay nuevos commits")
        repo.git.pull()
    except:
        logger.error("Some error occured while interacting with the repo")
        return False

    ## DOCKER
    client = docker.from_env()

    desired_container = get_stockfinder_container(client.containers.list())
    if not desired_container:
        logger.warning("Contener NGINX no encontrado (stockfinder_images)")
        return False
    logger.warning(f"Encontrado el contenedor deseado {desired_container.name} - {desired_container}")

    try:
        desired_container.restart()
    except:
        logger.error("Some error occured while trying to restart the contenedor")
        return False

    new_container = get_stockfinder_container(client.containers.list())
    if not new_container:
        logger.warning("Se ha reiniciado el contenedor, pero no ha levantando")
        return False
    logger.warning(f"Se ha reiniciado el contenedor y ha levantando {new_container.name} - {new_container}")

    return True


main()
