# aclue-dart-labeling

This repo contains a notebook and support files to generate artificial dart datasets.

The datasets consists of images of a dart board with 0-3 darts, and a label file which contains bounding box information (darts and anchor points)


### pre-commit-hook

To clean the output of the notebook, copy the pre-commit-hook script into the git folder.

`cp pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`