# VisBioMed 

This project aims to create a visual survey browser for articles which were pushed in Eurographics conference for Biology and Medicine
(2008 to 2021)


## Steps to run the project locally

Clone the repository
```commandline
git clone https://git.rwth-aachen.de/pruthvi.hegde/vis-bio-med.git
```

or 

```commandline
git@git.rwth-aachen.de:pruthvi.hegde/vis-bio-med.git
```


Navigate to `vis-bio-med` repository and activate your `venv` or `conda` environment.
Once your virtual environment is activated, run,

```commandline
pip install -r requirements.txt
```

### To run the website locally,

copy `BioWordVec_PubMed_MIMICIII_d200.txt` inside `filter/static/mlmodels` and to run django-server,
```commandline
python manage.py runserver
```