<h1 align="center">BioMedVis</h1>
<div align="center">
  <strong>BioMedVis project aims to create a visual survey browser for articles which were published in Eurographics conference on
Biology and Medicine
(2008 to 2021) </strong>
</div>

## Steps to run the project locally

Clone the repository

```commandline
git clone https://github.com/pruthvi-hegde/biomedvis.git
```

cd to `biomedvis` repository and activate your `venv` or `conda` environment. Once your virtual environment is
activated, run,

```commandline
pip install -r requirements.txt
```

### To run the website locally,

```commandline
python manage.py runserver
```

## For Developers

### Setup Django tables

1. There are 3 database tables on which website relies on. Those are : Article, Category, Subcategory
2. `article.py` and `category.py` inside `models` folder contains schema for the tables.
3. To create tables, run below commands from project top level directory

```commandline
python manage.py makemigrations
python manage.py migrate
```

### To add data to Database tables

1. Copy all thumbnails under `thumbnails` folder which is inside `articles_data` folder.
2. Copy `all_articles_metadata.json` from [VCBMCrawler repository](https://github.com/pruthvi-hegde/VCBMCrawler/) inside
   articles_data folder
3. Update `all_articles_metadata.json` with thumbnails path by running `update_articles_data` inside scripts folder.
   This will add local thumbnail path to each of the publication data.
4. Run `populate_db_tables` from project directory
5. The database tables should be now populates with the relevant data.
