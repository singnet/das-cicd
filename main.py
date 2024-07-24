import os
import github


def write_outputs(outputs: dict):
    with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
        for key, value in outputs.items():
            f.write(f"${key}={value}\n")


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

    conclusion = workflow.invoke(
        ref=git_reference,
        workflow_id=workflow_id,
    )

    write_outputs({"conclusion": conclusion})


if __name__ == "__main__":
    main()
