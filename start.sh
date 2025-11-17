cd ~/Thomas/firecan_repo
gnome-terminal -- ./venv/bin/ngrok http --domain=firecan.ngrok.app 5000
gnome-terminal -- ./venv/bin/python firecan_main.py
