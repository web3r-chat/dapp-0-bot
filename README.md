# dapp-0-bot

Our first Rasa chatbot for the Internet Computer.

The live deployment can be found at https://web3r.chat

The full application consists of 3 GitHub repositories:
1. [dapp-0](https://github.com/web3r-chat/dapp-0)
2. [dapp-0-django](https://github.com/web3r-chat/dapp-0-django)
3. [dapp-0-bot](https://github.com/web3r-chat/dapp-0-bot)

## Git

```bash
git clone git@github.com:web3r-chat/dapp-0-bot.git
cd dapp-0-bot
```

## Internet Identity

The action server makes authenticated calls to canister_motoko, using a dedicated internet identity.

- We used dfx to create the [dfx identity](https://smartcontracts.org/docs/developers-guide/cli-reference/dfx-identity.html) `dapp-0-bot-action-server`,  with the command:

  ```bash
  dfx identity new dapp-0-bot-action-server
  
  # The private key is stored in the file:
  # ~/.config/dfx/identity/dapp-0-bot-action-server/identity.pem
  ```

- We used dfx to specify that this identity uses our regular cycles wallet, with the commands:

  ```bash
  # Issue these commands from the web3r_chat repository
  dfx identity --network ic use dapp-0-bot-action-server
  dfx identity --network ic set-wallet aaaaa-aaaaa-aaaaa-aaaaa-aaa  # Replace with your wallet id !
  
  # Verify it is all ok
  dfx identity --network ic get-wallet 
  
  # Reset identity to default
  dfx identity --network ic use default
  ```

- We base64 encoded the pem file into a single line with the command:

  ```bash
  base64 -w 0 ~/.config/dfx/identity/dapp-0-bot-action-server/identity.pem
  ```

- We pass this value into our action server via the environment variable `BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED`

  - Locally, store it in `.env`

- We extract it in the file `actions/settings.py`

- We figured out the principal of this identity by calling the `whoami` method.

  - We updated the value for `_bot_0_action_server_principal` in the smart contract of the  `dapp-0` repository:

    ```javascript
    # file: dapp-0/src/backend/motoko/auth.mo
    
    public func is_django_server(p: Principal) : Result.Result<(), Http.StatusCode> {
        ...
        let _bot_0_action_server_principal : Principal = Principal.fromText("xxxx-xxxx-...");
    	...
    };
    ```

- Now we can use use [ic-py](https://github.com/rocklabs-io/ic-py) to make authenticated calls from the action server's python code to the protected APIs of the smart contract that is running in the motoko_canister on the Internet Computer.

## Secrets in `.env`

Create a `.env` file that looks like this:

```bash
#
# Only needed when deploying to Digital Ocean
# Access token is used to authenticate doctl with: make doctl-auth-init 
DIGITALOCEAN_ACCESS_TOKEN="..."

#
# JWT protection for socketio channel, using HS256
# Value must be equal to the SECRET_JWT_KEY value of the django_server
SECRET_JWT_KEY="..."
JWT_METHOD="HS256"

#
# Action server connection to local services
SECRET_JWT_KEY="..."
IC_NETWORK_URL="http://localhost:8000"
CANISTER_MOTOKO_ID="..."
CANISTER_MOTOKO_CANDID_UI="http://localhost:8000?canisterId=...&id=..."

#
# Action server internet identity
BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED="..."
```



To set the environment variables in your shell:

```bash
export $(cat .env | grep -v '#' | xargs)
```



## Conda

[Download MiniConda](https://docs.conda.io/en/latest/miniconda.html#linux-installers) and then install it:

```bash
bash Miniconda3-xxxxx.sh
```

Create a conda environment with Python:

Note: we use python 3.8, because the rasa-sdk is still at python 3.8

```bash
conda create --name dapp-0-bot python=3.8
conda activate dapp-0-bot

pip install --upgrade pip
pip install -r requirements-dev.txt
```



## Train the bot

```bash
rasa train --domain domain
```



## Test the bot

```bash
rasa test --domain domain
```

This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/test_stories.yml`. All tests must pass.



## Run the Rasa Server

```bash
# Set the environment variables in your shell
export $(cat .env | grep -v '#' | xargs)

# Run the rasa server
rasa run [--debug]
```



## Run the Action Server

```bash
# Set the environment variables in your shell
export $(cat .env | grep -v '#' | xargs)

# Run the action server
rasa run actions [--debug]
```



## Smoketest

```bash
make smoketest
```
