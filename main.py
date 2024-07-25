import os
import github


def write_outputs(outputs: dict):
    for key, value in outputs.items():
        print(f"::set-output name={key}::{value}")


def main():
    organization = os.getenv("GITHUB_ORG")
    repository = os.getenv("GITHUB_REPO")
    token = os.getenv("GH_TOKEN")
    workflow_id = os.getenv("GITHUB_WORKFLOW_ID")
    git_reference = os.getenv("GIT_REFERENCE")

    auth = github.Auth(
        token,
        organization,
        repository,
    )

    workflow = github.Workflow(auth)

    workflow_result = workflow.invoke(
        ref=git_reference,
        workflow_id=workflow_id,
    )

    write_outputs(workflow_result)


if __name__ == "__main__":
    main()
