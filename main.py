"""
Script for synchronizing directories.
"""

import colorlog
from termcolor import colored
import argparse
import os
import requests
import logging
from datetime import datetime
from xml.etree import ElementTree
import configparser


def setup_logging(log_level):
    """
    Setup logging configuration
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    ))
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(log_level)


def get_xml(url_path_on_server):
    """
    Fetch XML from server.
    """
    base_url = "https://is.muni.cz/auth/dok/fmgr_api?url="
    url = base_url + url_path_on_server
    auth = (os.getenv("IS_USERNAME"), os.getenv("IS_PASSWORD"))
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return ElementTree.fromstring(response.content)


def download_file(local_path, server_url_path, file_name):
    """
    Download file from server.
    """
    logging.debug(
        f"Starting download: Local path: {local_path}, Server URL path: {server_url_path}"
    )
    url = f"https://is.muni.cz/auth{server_url_path}{file_name}"
    response = requests.get(
        url, auth=(os.getenv("IS_USERNAME"), os.getenv("IS_PASSWORD"))
    )
    response.raise_for_status()

    # Ensure the directory exists
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "wb") as file_handle:
        file_handle.write(response.content)
    logging.info(f"Downloaded {file_name} to {local_path}")


def synchronize_directory(local_full_path, url_path_on_server):
    """
    Synchronize local and server directories.
    """
    logging.info(colored(f'Synchronizing directory: {url_path_on_server}', 'blue'))

    root = get_xml(url_path_on_server)
    total_files = len(root.findall(".//objekt"))
    downloaded_files = 0
    errored_files = 0



    for objekt in root.findall(".//objekt"):
        file_name = objekt.find("jmeno_souboru").text
        local_path = os.path.join(local_full_path, file_name)
        server_url_path = objekt.find("cesta").text.rsplit("/", 1)[0] + "/"
        try:
            server_mod_time = datetime.strptime(
                objekt.find("vlozeno").text, "%Y-%m-%dT%H:%M:%S"
            )
            logging.debug(
                f"Local path: {local_path}, Server URL path: {server_url_path}"
            )
            logging.debug(f"Server file {file_name} timestamp: {server_mod_time}")
            if os.path.exists(local_path):
                local_mod_time = datetime.fromtimestamp(os.path.getmtime(local_path))
                logging.debug(f"Local file {local_path} timestamp: {local_mod_time}")
                if server_mod_time > local_mod_time:
                    logging.info(f"Downloading updated file {file_name} from server.")
                    download_file(local_path, server_url_path, file_name)
                    downloaded_files += 1
                else:
                    logging.debug(f"File {file_name} is up to date.")
            else:
                logging.info(f"File {file_name} does not exist locally. Downloading now.")
                download_file(local_path, server_url_path, file_name)
                downloaded_files += 1
        except Exception as err:  # pylint: disable=broad-except
            logging.error(f"Error processing file {file_name}: {err}")
            errored_files += 1

    ok_files = total_files - errored_files - downloaded_files # Calculate OK files

    logging.info(f"{colored('Completion Status:', 'green')} "
                 f"Downloaded {colored(f'{downloaded_files}', 'cyan')}+"
                 f"{colored(f'{ok_files}', 'green')}/"
                 f"{f'{total_files}'} files with "
                 f"{colored(f'{errored_files}', 'red')} errors.")

    # return the number of errored files for later statistics
    return total_files, downloaded_files, errored_files


def main(config_path):
    """
    Main function to initiate synchronization.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = configparser.ConfigParser()
    config.optionxform = str # case senstive strings
    config.read(config_path)

    try:
        # Expand ~ to the user's home directory
        root_dir = os.path.expanduser(config['Settings']['ROOT_DIR'])
    except KeyError:
        logging.critical("Missing 'ROOT_DIR' in 'Settings' section of the config file.")
        return
    except Exception as e:
        logging.critical(f"Unknown error, report to upstream: {e}")
        return

    errors = []
    total_files = 0
    total_downloaded = 0
    total_errors = 0

    if 'Channels' not in config:
        logging.error("Missing 'Channels' section in the config file. Nothing to sync.")
        return

    channel_count = len(config['Channels'].items())

    for local_relative_path, url_path_on_server in config['Channels'].items():
        local_full_path = os.path.join(root_dir, local_relative_path.lstrip('/'))
        [total,downloaded,error] = synchronize_directory(local_full_path, url_path_on_server)
        total_files += total
        total_downloaded += downloaded
        total_errors += error
        if (error > 0):
            errors.append(local_relative_path)


    ok_files = total_files - total_errors - total_downloaded


    logging.info("="*79)
    logging.info(colored(f"Synchronized {channel_count-len(errors)}/{channel_count} channels, ", "white") +
                     f"{len(errors)} error(s)")
    if errors:
        logging.warning(f"Failed channels: {', '.join(errors)}).")

    logging.info(f"{colored('Synchronization result:', 'green')} "
                 f"Downloaded {colored(f'{total_downloaded}', 'cyan')}+"
                 f"{colored(f'{ok_files}', 'green')}/"
                 f"{f'{total_files}'} files with "
                 f"{colored(f'{total_errors}', 'red')} errors.")


if __name__ == "__main__":
    ARGS_PARSER = argparse.ArgumentParser(description='Directory synchronization script.')
    ARGS_PARSER.add_argument(
        "--log",
        default="INFO",
        help="Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    ARGS_PARSER.add_argument(
        "--config",
        default="config.ini",
        help="Path to the config.ini."
    )
    ARGS = ARGS_PARSER.parse_args()
    setup_logging(ARGS.log)
    main(ARGS.config)
