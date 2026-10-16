mv /tmp/weekly_delete.log /tmp/weekly_delete.bak
cd /home/ubuntu/web/stocks
/home/ubuntu/.venv/bin/python3 weekly_clean.py
