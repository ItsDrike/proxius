# PROXIUS

Proxius is a chat software made in Python 3.

## Usage

Proxius is by default set to use localhost (127.0.0.1) IP address.<br>
If you want to use other IP (to connect outside your local machine),
you need to change **IP** in `config.conf` file.<br>
You should also change the **PORT** in `config.conf` to whatever you like.<br>

After you are happy with the configuration, install the requirements for python:
```sh
python3 -m pip install -r requirements.txt
```

Now you can run `server.py`:

```sh
python3 server.py
```

This will initialize the server when it is ready your clients can connect using

```sh
python3 client.py <Host IP> <PORT> <password> <username>
```

Currently, there is no use for *password*, but in the future Encryption will be added.

## Future

Proxius will be a fully encrypted and secure way to send messages to others.
