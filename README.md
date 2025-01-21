# Srun Network Auto Login Decryptor  
This program is designed to crack the login function of the Srun network management system. Using this program makes it possible to log in to the Srun network using command-line and other methods.  

Note: **This program has been optimized specifically for the Srun network management system at Shenzhen University**  

## Features  

- [x] **Automatic Login**: Automatically log in to the network when the network is disconnected  
- [x] **Single Login**: Just login the network for once, typically used for login in the server terminal  
- [x] **Fully Support System Proxy**: Support HTTP and HTTPS proxy settings, can be used in a network environment with proxy
- [x] **DNS Compatibility**: Compatible with DNS settings, can be used in a network environment with customized DNS settings
- [ ] **ACID Auto Detection**: Automatically detect the ACID value of the network login page, no need to manually find it

## File Introduction  
- **dist**: Contains compiled executable files  
- **logs**: Program log storage area  
- **Mode**: Program mode execution logic storage area  
    - **Client**: Client mode operation logic (not implemented)  
    - **Server**: Server mode operation logic (not implemented)  
    - **Manual**: Manual mode operation logic  
- **SrunLogin**: Srun network login decryption logic  
    - **Encryption**: Encryption logics  
    - **__init__.py**: Main operation logic  
- **Utils**: Tool logic storage area  
    - **Online.py**: Network online detection logic  
- **log.py**: Program log management logic  
- **main.py**: Program entry file  
- **README.md**: Program introduction file  
- **requirements.txt**: Program dependency file  
- **single.py**: Just login the network for once  

## Usage  
This program has two main ways of running: using executable files to run, and directly running Python source code to run.  
- Executable Type  
    - Network Protector Mode:  
    *Automatically log in to the network when the network is disconnected*  
    - Single Login Mode:  
    *Just login the network for once*  
- Python Source Code Type  
    - Network Protector Mode:  
    *Automatically log in to the network when the network is disconnected*  
    - Single Login Mode:  
    *Just login the network for once*  
### Use Executable File  
Just run it directly, please note that `config.yaml` must be placed in the same directory as the executable file.  
#### Network Protector Mode
In this mode, you need to modify your personal information in the `config.yaml` file, like username and password.  
- **Windows**: Run following command in CMD will start the program:  
    Note: `config.yaml` must be in the same directory of `Srun_windows_x64.exe`  
    - `$ ./Srun_windows_x64.exe`  
    - `$ ./Srun_windows_x64.exe --manual`  
- **Linux**: Run following command in terminal will start the program (choose one of the command):  
    Note: `config.yaml` must be in the same directory of `Srun_ubuntu_x64`  
    - `$ ./Srun_ubuntu_x64`  
    - `$ ./Srun_ubuntu_x64 --manual`  
#### Single Login Mode
- **Windows**: Run following command in CMD will let the current machine login to the network:  
    Note: `config.yaml` must be in the same directory of `SrunLogin_windows_x64.exe`  
    - `$ ./SrunLogin_windows_x64.exe -u <username> -p <password>`
- **Linux**: Run following command in terminal will let the current machine login to the network:  
    Note: `config.yaml` must be in the same directory of `SrunLogin_ubuntu_x64`  
    - `$ ./SrunLogin_ubuntu_x64 -u <username> -p <password>`
### Run Python Source Code  
In this operating mode, there are two modes to choose from: protection mode and single mode.  
- In **PROTECTOR** mode, when the program detects that network connectivity has failed, it will automatically call the login cracker to log in to the network.  
- In **Single** mode, only one cracking command will be sent for network login without ensuring connectivity  

Note: For both modes, the `config.yaml` file must be placed in the same directory as the program. The detailed configuration method is described in the `config.yaml` file.  

#### PROTECTOR Mode  
- Install the required dependencies:  
    - `$ pip install -r requirements.txt`  
- Modify the configuration file `config.yaml` according to the actual situation (details in following chapters)  
- Run the program (choose one of the command):  
    - `$ python main.py --manual`  
    - `$ python main.py` (If you set `settings.default_mode` to `0` in `config.yaml`)  
#### Single Mode  
- Install the required dependencies:  
    - `$ pip install -r requirements.txt`  
- Modify the configuration file `config.yaml` according to the actual situation (details in following chapters)  
- Run the program:  
    - `$ python single.py -u <username> -p <password>`  

## Configuration File  
For the configuration file, there are several areas that need to be modified according to your actual network situation and personal situation. The specific significance of the configuration project has been indicated in the document through annotations.  
- **MUST** be modified:  
    - `auth.username`:  
    Please fill in your username  
    - `auth.password`:  
    Please fill in your password  
- **Optional** modification:  
    - `settings.request_timeout` [unit: second(s)]:  
    Request timeout settings, default is 2 seconds. You can adjust according to the network speed. The less the value is, the shorter the time given to the server to respond. Do not set it too low, otherwise, the server may not have enough time to respond.  
    - `settings.online_check_duration` [unit: second(s)]:  
    The interval between each network online detection, default is 5 seconds. You can adjust according to your needs. The smaller the value is, the faster the program can detect network disconnection, the shorter the time to reconnect. But if the value is too small, it may cause the program to consume too much CPU resources, and sent too many requests to the server. May cause the server to block your IP.  
    - `logger.file.enable`:  
    If you do not want to save the log file, you can set it to `False`.

## SrunLogin Module  
Of course, the SrunLogin module is written with the call in mind. It can be imported as a module by other Python files. The specific calling method is as follows:  
- Copy the `SrunLogin` folder to the directory where the Python file is located  
- Import the module in the Python file:  
    ```python
    from SrunLogin import SrunLogin
    ```  
- Instantiate a SrunLogin object:  
    ```python
    srun = SrunLogin(
        [login_page_url,            # Login page URL
        challenge_api_url,          # Challenge API URL
        login_api_url,              # Login API URL
        callback_parse_regex,       # Callback page parse regex
        page_parse_regex,           # Login page parse regex
        callback_str,               # Callback string (all fine unless its empty)
        skip_ssl_verify,            # Skip SSL verification when sending requests
        timeout,                    # Request timeout
        add_time_stamp_to_callback, # Add timestamp to callback string
        login_success_key,          # Key of login success value
        login_success_value,        # Value of login success key
        nameservers,                # Nameservers when sending requests
        hosts,                      # Hosts when executing local DNS resolution
        login_fixed_parameters,     # Fixed parameters when sending login requests  (More details in config.yaml)
        user_agent,                 # User-Agent when sending requests
        http_proxy,                 # HTTP Proxy when sending requests
        https_proxy]                # HTTPS Proxy when sending requests
    )
    ```  
    Note: **All parameters during instatntiate is optional, unless portal server settings is changed.**  
- Call the login function  
    ```python
    state, state_info, full_info = srun.login(
        username,   # Username
        password    # Password
    )
    ```  
    Three of the return values have the following meanings  
    - `state`: Login status, `True` means login successful, `False` means login failed  
    - `state_info`: Login status information returned by the server, `Dict` type.  
    - `full_info`: Full login information returned by the server, `Dict` type. Contains all information (variables, responses) during the login process  

## Posible Problems
Some problems may occur during the use of the program, and the following are some possible solutions:
- **All checks are failed, but network is fine**:
    - Possible reasons:
        - `settings.request_timeout` has been set too low, causing the server to not respond in time.
        - `settings.online_check_duration` has been set too low, causing the program to send too many requests to the server in a short time. May cause the server to block your IP for a period of time.
    - Solution:
        - Increase the value of `settings.request_timeout` in `config.yaml`.
        - Increase the value of `settings.online_check_duration` in `config.yaml`, and wait for a while to see if the network online checker is reconnected.
- **Login Failure**:
    - Possible reasons:
        - The username or password is incorrect.
        - The ACID is incorrect.
        - Modified the `login_fixed_parameters` in `config.yaml` incorrectly.
        - The server has changed the login encryption method.
    - Solution:
        - Check if the username and password are correct.
        - You can try to verify the ACID and modify the `login_fixed_parameters` in `config.yaml` follow the `ACID` chapter.
        - Reset the `login_fixed_parameters` in `config.yaml` to the default value.
        - If the server has changed the login encryption method, there is no way to solve it unless you can find the new encryption method.

## ACID
`ACID` is used as a key parameter in the login encryption process. The change will result in changes to the password hash value, information hash value, and checksum. Please follow the following process to determine if your `ACID` is correct. If it does not match the value `meta.portal.login_parameters.acid` in the `config.yaml` file, please modify it.  
**MAKE SURE YOUR NETWORK IS NOT LOGGED IN**  
1. Visit the following website, it will automatically redirect to a login page  
`https://net.szu.edu.cn/`  
2. After redirected you will see a URL like this:  
![URL-Redirected](./docs/Redirected-URL.png)  
3. Now you can find the `ACID` value in the URL, it is the value after `ac_id=` and before `&theme`.  
![ACID-Value](./docs/ACID-Position.png)  
4. Compare the value you get with the value `meta.portal.login_parameters.acid` in the `config.yaml` file. If they are different, please modify the value in the `config.yaml` file.  
