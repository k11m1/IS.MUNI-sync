# IS.MUNI-sync

A script to synchronize directories from IS.MUNI to your local machine.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/IS.MUNI-sync.git
    cd IS.MUNI-sync
    ```

2. Copy the example configuration file and customize it:
    ```bash
    cp config.ini.example config.ini
    ```

3. Open `config.ini` in your favorite text editor and update the values as needed. Here's a brief explanation of each setting:

    - `ROOT_DIR`: The root directory on your local machine where the synchronized directories will be stored. 
    - `LOG_LEVEL`: The logging level for script execution. Valid values are *DEBUG*, *INFO*, *WARNING*, *ERROR*, and *CRITICAL*.
    - Under `[Channels]`, each entry represents a channel you want to synchronize. The key is the name of the local directory (relative to `ROOT_DIR`), and the value is the path on the server after `https://is.muni.cz/auth/`.

    Example:
    ```ini
    [Settings]
    ROOT_DIR = ~/muni_sync
    LOG_LEVEL = INFO

    [Channels]
    IA174 = /el/fi/podzim2023/IA174/um/slides_plain/before_lecture/
    PV079 = /el/fi/podzim2023/PV079/um/lectures/
    # Add more directories as needed
    ```

4. Set up environment variables for authentication:
    - `IS_USERNAME`: Your non-personal UCO.
    - `IS_PASSWORD`: Your non-personal is.muni.cz password.

    It's recommended to use a non-personal account for this synchronization to ensure security, but your personal account will work. See the IS.MUNI API in the IS help for more information. 

    ```bash
    export IS_USERNAME='your-username'
    export IS_PASSWORD='your-password'
    ```

5. Run the script:
    ```bash
    python3 main.py
    ```

## Usage

```bash
usage: main.py [-h] [--log LOG] [--config CONFIG]

Directory synchronization script.

optional arguments:
  -h, --help       show this help message and exit
  --log LOG        Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --config CONFIG  Path to the config.ini.
```
