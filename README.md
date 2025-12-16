# Srun Network Auto Login Decryptor  
This program is designed to crack the login function of the Srun network management system. Using this program makes it possible to log in to the Srun network using command-line and other methods.  

Note: **This program has been optimized specifically for the Srun network management system at Shenzhen University**  

## Features  

- [x] **Automatic Login**: Automatically log in to the network when the network is disconnected  
- [x] **Single Login**: Just login the network for once, typically used for login in the server terminal  
- [x] **Fully Support System Proxy**: Support HTTP and HTTPS proxy settings, can be used in a network environment with proxy
- [x] **DNS Compatibility**: Compatible with DNS settings, can be used in a network environment with customized DNS settings
- [x] **ACID Auto Detection**: Automatically detect the ACID value of the network login page, no need to manually find it

## File Introduction  
- **logs**: Program log storage area (this folder will be created automatically when the program is executed)  
- **SrunLogin**: Srun network login decryption logic  
    - **Encryption**: Encryption logics  
    - **__init__.py**: Main operation logic  
- **Log.py**: Program log management logic  
- **Config.py**: Program configuration management logic
- **main.py**: Program entry file  
- **README.md**: Program introduction file  
- **requirements.txt**: Program dependency file  

## Usage  
This program has two main ways of running: using executable files to run, and directly running Python source code to run.  
If there is no `config.yaml` file in the same directory, the program will create a default `config.yaml` file.  
### Run Python Source Code Directly (Recommended)  
- Prepare the python environment, `Python 3.12+` is recommended.  
- Install the required dependencies as follows or simply run `$ pip install -r requirements.txt`:  
    - `dnspython >= 2.7.0`: For local DNS resolution  
    - `pyyaml >= 25.1.0`: For configuration file parsing  
    - `requests >= 2.32.3`: For network requests  
    - Lower version may also work but are not recommended, you can try it by yourself  
- Clone the repository `git clone https://github.com/Aurora211/SrunLogin-for-SZU`  
- Run the program: there are two modes of operation, which are `daemon` mode and `manual` mode.  
    - `daemon` mode: Run `$ python main.py --daemon -u <username> -p <password>`  
      In this mode, the program will run in the background and will automatically login to the network when the network is disconnected.  
      If you want to run it in the background, you can run it in the background with the command `$ nohup python main.py --daemon -u <username> -p <password> > /dev/null 2>&1 &`.
    - `manual` mode: Run `$ python main.py -u <username> -p <password>`  
      In this mode, the program will only login once and exit.  

### Use Executable File  
Just run it directly, please note that `config.yaml` must be placed in the same directory as the executable file.  
If there is no `config.yaml` file in the same directory, the program will create a default `config.yaml` file.  

- `Daemon` Mode:
    - Run `$ ./SrunSZU_Ubuntu_64bit_v2.0 --daemon -u <username> -p <password>` on Ubuntu  
    - Run `$ ./SrunSZU_Windows_64bit_v2.0.exe --daemon -u <username> -p <password>` on Windows
    - In this mode, the program will run in the background and will automatically login to the network when the network is disconnected.  
    - If you want to run it in the background, you can run it in the background with the command `$ nohup ./SrunLogin-for-SZU --daemon -u <username> -p <password> > /dev/null 2>&1 &`.
- `Manual` Mode:
    - Run `$ ./SrunSZU_Ubuntu_64bit_v2.0 -u <username> -p <password>` on Ubuntu  
    - Run `$ ./SrunSZU_Windows_64bit_v2.0.exe -u <username> -p <password>` on Windows
    - In this mode, the program will only login once and exit.

Note: For both modes, the `config.yaml` file must be placed in the same directory as the program. The detailed configuration method is described in the `config.yaml` file.  

## Configuration File  
For the configuration file, there are several areas that need to be modified according to your actual network situation and personal situation. The specific significance of the configuration project has been indicated in the document through annotations.  
- **Optional** modification:  
    - `auth.username`:  
    Please fill in your username, if the username is not filled in, the program will ask you to enter the username.  
    - `auth.password`:  
    Please fill in your password, if the password is not filled in, the program will ask you to enter the password.  
    - `auth.lan`:
    Select the ethernet mode, set `True` to use the szu-lan internal network only.
    - `settings.timeout` [unit: second(s)]:  
    Request timeout settings, default is 2 seconds. You can adjust according to the network speed. The less the value is, the shorter the time given to the server to respond. Do not set it too low, otherwise, the server may not have enough time to respond.  
    - `settings.duration` [unit: second(s)]:  
    The interval between each network online detection, default is 5 seconds. You can adjust according to your needs. The smaller the value is, the faster the program can detect network disconnection, the shorter the time to reconnect. But if the value is too small, it may cause the program to consume too much CPU resources, and sent too many requests to the server. May cause the server to block your IP.  

## SrunLogin Module  
Of course, the SrunLogin module is written with the call in mind. It can be imported as a module by other Python files. The specific calling method is as follows:  
- Copy the `SrunLogin` folder to the directory where the Python file is located  
- Import the module in the Python file:  
    ```python
    from SrunLogin import SrunLogin
    ```  
- Instantiate a SrunLogin object:  
    ```python
    srun: SrunLogin = SrunLogin(
        portal_config: Dict[str, Any],          # Srun Portal Configuration
        parameters: Dict[str, Dict[str, Any]],  # [Optional] Request Fixed Parameters
        parse_regex: Dict[str, str],            # [Optional] Page Parsing Regular Expressions
        nameservers: List[str],                 # [Optional] Upstream DNS Server
        hosts: Dict[str, List[str]]             # [Optional] Hostname Mapping
        proxies: Dict[str, Union[str, None]]    # [Optional] Proxies for requests
    )
    ```  
    Note: Except for `portal_config`, **all parameters during instatntiate is optional, unless portal server settings is changed.**  
- Call the login function  
    ```python
    state, message = srun.login(
        username: str,  # Username
        password: str,  # Password
        lan: bool       # Ethernet LAN mode
    )
    ```  
    Two of the return values have the following meanings  
    - `state[bool]`: Request status, `True` means request is sent successful, `False` means errors accurred during the request  
    - `message[Union[str|None]]`: Request message  
- Call the status function
    ```python
    state, info, full_info = srun.status()
    ```
    Three of the return values have the following meanings  
    - `state[bool]`: Ethernet status, `True` means ethernet is logged in, `False` means ethernet is not logged in  
    - `info[Dict[str, Any]]`: Status information  
    - `full_info[Dict[str, Any]]`: Full status information

## Posible Problems
Some problems may occur during the use of the program, and the following are some possible solutions:

- **Login Failure**:
    - Possible reasons:
        - The username or password is incorrect.
        - The ACID auto detection is failed, restart the program. (If problem still exists, you can start an issue in the GitHub.)
        - The server has changed the login encryption method. (This is not a problem, you can start an issue in the GitHub.)
    - Solution:
        - Check if the username and password are correct.
        - You can try to verify the ACID is the same as the one you see on your browser.
        - If the server has changed the login encryption method, there is no way to solve it unless you can find the new encryption method or wait for me to update the program.

## ACID
**Now the program has ability to automatically detect the `ACID` value. So you don't need to worry about it now. This section is only for debugging.**

`ACID` is used as a key parameter in the login encryption process. The change will result in changes to the password hash value, information hash value, and checksum. Please follow the following process to determine if your `ACID` is correct. If it does not match the value `meta.portal.login_parameters.acid` in the `config.yaml` file, please modify it.  
**MAKE SURE YOUR NETWORK IS NOT LOGGED IN**  
1. Visit the following website, it will automatically redirect to a login page  
`https://net.szu.edu.cn/`  
2. After redirected you will see a URL like this:  
![URL-Redirected](./docs/Redirected-URL.png)  
3. Now you can find the `ACID` value in the URL, it is the value after `ac_id=` and before `&theme`.  
![ACID-Value](./docs/ACID-Position.png)  
4. Compare the value you get with the value `meta.portal.login_parameters.acid` in the `config.yaml` file. If they are different, please modify the value in the `config.yaml` file.  
