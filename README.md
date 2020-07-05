# PROXIUS

Proxius is a secure chat software made with Python 3.

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

## How does it work

Proxius is a secure way of sending and receiving messages relayed by the server.
It is end-to-end encrypted which means the server can't read what cliens are sending.
It also generates new RSA512 keypair for every client which is used to identify him, this is useful for verification purposes as it prevents anyone else to pretend he's someone else.

If you're interested in a more detailed explanation, check this diagram:
![Flowchart](https://user-images.githubusercontent.com/20902250/86537150-355c7600-beed-11ea-9d04-cafd1b4b6721.png)


