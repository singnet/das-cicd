import requests
import time
import json


class Auth:
    def __init__(self, token, org, repo) -> None:
        self._token = token
        self.org = org
        self.repo = repo

    def get_authenticated_header(self):
        return {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }


class Workflow:
    def __init__(self, auth: Auth):
        self._auth = auth

    def _get_dispatch_url(self, workflow_id: str):
        return f"https://api.github.com/repos/{self._auth.org}/{self._auth.repo}/actions/workflows/{workflow_id}/dispatches"

    def _get_runs_url(self, workflow_id: str):
        return f"https://api.github.com/repos/{self._auth.org}/{self._auth.repo}/actions/workflows/{workflow_id}/runs"

    def _get_run_url(self, run_id: str):
        return f"https://api.github.com/repos/{self._auth.org}/{self._auth.repo}/actions/runs/{run_id}"

    def _get_jobs_url(self, run_id: str):
        return f"https://api.github.com/repos/{self._auth.org}/{self._auth.repo}/actions/runs/{run_id}/jobs"

    def _dispatch_workflow(self, ref: str, workflow_id: str):
        url = self._get_dispatch_url(workflow_id)

        data = {"ref": ref}

        response = requests.post(
            url,
            headers=self._auth.get_authenticated_header(),
            json=data,
        )

        if response.status_code == 204:
            print(
                f" Successfully started workflow with ID: {workflow_id} on the repository: {self._auth.repo}."
            )
        else:
            print(
                f"Failed to start workflow with ID: {workflow_id} on the repository: {self._auth.repo}."
            )
            print(response.text)
            response.raise_for_status()

    def _get_latest_run_id(self, workflow_id: str):
        url = self._get_runs_url(workflow_id)

        response = requests.get(url, headers=self._auth.get_authenticated_header())

        if response.status_code == 200:
            runs = response.json()
            run_id = runs["workflow_runs"][0]["id"]
            print(
                f"Workflow run retrieved. Details:\n  - Owner: {self._auth.org}\n  - Repository: {self._auth.repo}\n  - Workflow ID: {workflow_id}\n  - Run ID: {run_id}"
            )
            return run_id
        else:
            print("Failed to retrieve workflow run ID.")
            print(response.text)
            response.raise_for_status()

    def _get_run(self, run_id: str):
        response = requests.get(
            self._get_run_url(run_id),
            headers=self._auth.get_authenticated_header(),
        )
        if response.status_code == 200:
            return response.json()
        
        print("Failed to retrieve workflow run status.")
        print(response.text)
        response.raise_for_status()



    def _wait_for_completion(self, run_id: str, interval: int = 30):
        while True:
            run = self._get_run(run_id)
            print(f"Current status of workflow run ID {run_id}: {run['status']}")
            if run["status"] == "completed":
                conclusion = run["conclusion"]
                print(
                    f"Workflow run with ID {run_id} has completed with conclusion: {conclusion}"
                )
                return run["conclusion"], run
            else:
                time.sleep(interval)

    def _get_failed_jobs(self, run_id: str):
        url = self._get_jobs_url(run_id)
        response = requests.get(url, headers=self._auth.get_authenticated_header())
        failed_jobs = []

        if response.status_code != 200:
            print("Failed to retrieve Jobs list.")
            print(response.text)
            response.raise_for_status()

        try:
            jobs = response.json().get("jobs", [])
        except ValueError:
            print("Invalid JSON response.")
            return []

        for job in jobs:
            if job.get("conclusion") == "failure":
                for step in job.get("steps", []):
                    if step.get("conclusion") == "failure":
                        failed_jobs.append(
                            {
                                "url": job["html_url"],
                                "failed_at": step["name"],
                            }
                        )

        return failed_jobs

    def _format_failed_jobs_display(self, failed_jobs):
        if not isinstance(failed_jobs, list):
            raise ValueError("Expected 'failed_jobs' to be a list")

        failed_jobs_display = "\n".join(
            [f"- {job['failed_at']}: {job['url']}" for job in failed_jobs]
        )

        return failed_jobs_display

    def invoke(self, ref: str, workflow_id: str):
        self._dispatch_workflow(ref, workflow_id)
        time.sleep(10)
        run_id = self._get_latest_run_id(workflow_id)
        conclusion, run = self._wait_for_completion(run_id)

        workflow_response = {
            "run_url": run["html_url"],
            "run_id": run_id,
            "conclusion": conclusion,
            "failed_jobs_display": None,
            "failed_jobs": None,
        }

        if conclusion != "success":
            failed_jobs = self._get_failed_jobs(run_id)
            workflow_response["failed_jobs"] = json.dumps(failed_jobs)
            workflow_response["failed_jobs_display"] = self._format_failed_jobs_display(
                failed_jobs
            )

        return workflow_response
