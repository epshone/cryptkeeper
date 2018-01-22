#Install pipenv
pip install --user pipenv

#Install the binance API
pip install python-binance

# find directory
SITEDIR=$(python -m site --user-site)

# create if it doesn't exist
mkdir -p "$SITEDIR"

CURRENTPATH=$(pwd)

# create new .pth file with our path
echo "$CURRENTPATH" > "$SITEDIR/cryptkeeper.pth"