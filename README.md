### Photography blog

Author: Arnab Laha & Claude AI

I envisioned this package to be fully automated using various config yaml files. The main ingredients are:
- `config:` It consists of three config files that control the three main page contents (index, photography, and blog)
- `site_builder:` It contains the navigation style, CSS, and Python macros to build the pages
- `build.py:` Main Python macro that builds the website (`python3 build.py`) by using config and site_builder

```
config/
├── blog.yaml
├── main.yaml
├── photography.yaml
storage/
└── blogs
    └── blog1.html
site_builder/
├── __init__.py
├── nav.py
├── pages
│   ├── blog_page.py
│   ├── index_page.py
│   ├── __init__.py
│   ├── photo_page.py
└── styles.py
build.py
```

Utility macros
- `cloudinary_sync.py:` I host images in my Cloudinary account. This API based macro helps me to sync the Cloudinary images and build the photography.yaml config

Storage area
- `storage:` It serves as a storage area for my blogs and other residual files or images pertinent to this website

Contact: alahahep@gmail.com

Site-url: https://alaha999.github.io/OverwrittenMemories/

Share your thoughts with me if you appreciate the content! I would be happy to connect!
