# User Manual to Install: Using a VISA ILL Machine assuming no GitHub and no permission to run bash scripts

1. Download zip version
2. Extract all content into a desired folder
3. Using the terminal cd into the desired folder
4. Once in the folder run `python -m venv venv`
5. Activate venv via `source venv/bin/activate`
6. Install required dependencies via `pip install -r requirements.txt`
7. In case VISA download limits become a problem run inside the terminal `while ! pip install -r requirements.txt --timeout 300; do
  echo "Install failed, retrying..."
  sleep 5
done`
If the download gets stuck use Control + C to abort operation and wait again for the process to repeat itself.
8. Once the venv has been set up access the ToScaNA GUI via `panel serve app.py --address localhost --port 5006 --show
`
