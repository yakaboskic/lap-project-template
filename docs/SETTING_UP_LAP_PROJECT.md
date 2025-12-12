# Setting up a LAP Project
## Setup of Web UI
To setup a web UI go to your home directory and create or add to your `private_html` directory with the following commands:
```bash
$ ln -s project-name /path/to/project/out
```
Then go to your project directory and make the raw and out directories have these permissions
```bash
cd /path/to/project
chmod -R o+rX out raw
```
