#Install pipenv
pip install --user pipenv

#Install the binance API
pip install python-binance

# find directory
SITEDIR=$(python -m site --user-site)

# create if it doesn't exist
mkdir -p "$SITEDIR"

# get the directory
CURRENTPATH=$(pwd)

# create new .pth file with our path
echo "$CURRENTPATH" > "$SITEDIR/cryptkeeper.pth"

# create credentials file if it doesn't exist
if [ -f credentials.json ]; then
   echo "credentials.json already exists"
else
   echo "creating file credentials.json"
   touch credentials.json
   echo "{" >> credentials.json
   echo "    \"API_KEY\": \"\"," >> credentials.json
   echo "    \"API_SECRET\": \"\"" >> credentials.json
   echo "}" >> credentials.json
fi
