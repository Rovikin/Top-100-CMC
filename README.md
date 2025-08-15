# Top-100-CMC
Displaying data of 100 top marketcap based on Coinmarketcap using python in termux.
### INSTALATION
install termux from playstore or from f-droid or from anywhere that provides termux application for android. then follow this command in termux terminal:

```
pkg update
pkg upgrade
pkg install python
pkg install python-pip
pip install requests
cd /sdcard/
git clone https://github.com/Rovikin/Top-100-CMC.git
cd /sdcard/Top-100-CMC
nano top_100_cmc.py
```

on line 5 (API_KEY = 'YOUR-API-KEY') replace 'YOUR-API-KEY' with your Coinmarketcap personal API. Go to Coinmarketcap site to get your API.

After changing your API, please save it by clicking ctrl+o+enter and then clicking ctrl+x.

After that, please run it using the command:

```
python top_100_cmc.py

```
## Update For C++

I've added new support for the C++ version. This time, you don't need a CMC API key. I'm using the Coingecko API. You can see there is a '100.cpp' file there.

Follow these commands to compile it:
```cpp
g++ -std=c++17 -o 100 100.cpp -lcurl
```
untuk menjalankannya cukup ketik:
```shell
./100
```
