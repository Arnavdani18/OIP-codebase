#!/bin/bash
cd ~/frappe-bench/apps/contentready_oip
git pull
bench --site master.openinnovationplatform.org migrate
cd ..
find . -iname *.pyc -delete
bench restart
