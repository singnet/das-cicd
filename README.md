# DAS CI/CD

Github action libraries used in all DAS repos' pipelines

## Workflow Setup

To implement this workflow in your repository, follow these steps:

1. Copy and paste the following YAML content into the workflow file:

```yaml
name: My Workflow

on:
  workflow_dispatch:
    inputs:

jobs:
  tag:
    uses: singnet/das-cicd@master
    with:
      workflow: run-tests.yml
      repo: das-atom-db
      org: singnet
      ref: master
      github-token: ${{ secrets.GH_TOKEN }}
```

2. Customize the variables in the same way to fit your project's requirements.
