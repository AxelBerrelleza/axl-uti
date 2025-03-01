Step to start developing
1. python -m venv .venv
2. source .venv/bin/activate
3. python -m pip install --upgrade pip
4. pip install -r requirements.txt
5. then you can run `python main.py --help`

### About the symbols.py file
The structure of the file is just a python dictionary, as follows:
```python
symbols: dict = {
  "AMZN": "0P000000B7",
}
```
This way you can use commands normally, just: ´axl-uti stocks fundamentals AMZN´

Otherwise: ´axl-uti stocks fundamentals --pid 0P000000B7´