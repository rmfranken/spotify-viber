#shell script to run this everyday, adjust your source to the path of your venv and the path of your main.py

#then make sure to make this file executable by running chmod +x run-spotify-viber.sh
#then add this to your crontab by running crontab -e and adding the following line:
#0 0 * * * /path/to/your/run-spotify-viber.sh
#this will run the script every day at midnight
#you can change the time by changing the first two numbers, the first one is the minute and the second one is the hour


#!/bin/bash
source /home/rmfranken/standardPythonEnvironment/bin/activate
python /home/rmfranken/spotify-viber/main.py >> /home/rmfranken/spotify-viber/script.log 2>&1