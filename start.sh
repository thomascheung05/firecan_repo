cd ~/Thomas/firecan_repo
gnome-terminal -- ./venv/bin/instatunnel connect 5000 --subdomain firecan --api-key it_6c1e405459eb827f455357a73338031c99a207936e1a0f8b45e5c507deb8
gnome-terminal -- ./venv/bin/python firecan_main.py
while true; do
  curl -s https://firecan.instatunnel.my/ > /dev/null
  sleep 60  # ping every 4 minutes
done
