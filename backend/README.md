# Tip Reporter Scenario


## Getting Started
1. Copy the file `.env.example` into a new file called `.env`. Set the value of the Square Access Token for the sandbox account you want to seed data into. 

```
SQUARE_SANDBOX_ACCESS_TOKEN=yourSandboxAccessToken
```

2. Create a python virtual environment, activate it, and install dependencies
```
$ python3 -m venv ./venv
$ . ./venv/bin/activate
$ pip3 install -r requirements.txt
```

3. Seed test data into a sandbox seller account
```python
$ python seed-data.py --seed
```

4. Start server
```python
`python -m flask run`
```
