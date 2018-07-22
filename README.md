Image search
============

Demo for the talk *Searching images in Elasticsearch using Luminoth*.

Instalation
-----------

Run with:

```
$ docker-compose build
$ docker-compose up elasticsearch
$ docker-compose up api frontend
```

Then go to http://localhost:3000.

Uploading images
----------------

You can upload images through the frontend. Alternatively, bulk upload
all images in a folder by running:

```
$ ls images | xargs -I % curl 'http://localhost:5050/store/' -F 'image=@images/%'
```