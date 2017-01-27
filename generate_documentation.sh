#!/usr/bin/env bash -x
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pip install -r requirements-docs.txt
cd ./docs
make html

TARGET_BRANCH="gh-pages"
mkdir ${TARGET_BRANCH}
cd ${TARGET_BRANCH}
 
git clone -b ${TARGET_BRANCH} --single-branch https://github.com/ironSource/atom-python.git

cd atom-python
cp -r ../../build/html/* .

git add .
git commit -m "Deploy to GitHub Pages"

# Now that we're all set up, we can push.
git push origin ${TARGET_BRANCH}

cd ../../
rm -r -f ${TARGET_BRANCH}
