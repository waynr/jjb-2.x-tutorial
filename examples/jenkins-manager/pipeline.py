import jenkins_manager.types.job as job
import jenkins_manager.types.pipeline as pipeline


class BaseJob(job.TemplateJob):

    def __init__(self, *args, **kwargs):
        super(BaseJob, self).__init__(*args, **kwargs)
        self["name"] = "jenkins-manager__{{type}}__{{git_branch}}"
        self["display-name"] = "jenkins-manager {type}}__{{git_branch}}"

        self["scm"] = [{
            "git": {
                "url": "https://github.com/waynr/jenkins-manager",
                "skip-tag": True,
                "branches": [
                    "{{git_branch}}",
                ],
            },
        }]

        self.update(kwargs)


class PythonJob(BaseJob):

    version_string_map = {
        "2.7": "System-CPython-2.7",
        "3.4": "System-CPython-3.4",
    }

    def __init__(self, *args, **kwargs):
        if "python_version" not in kwargs:
            kwargs["python_version"] = "2.7"
        python_version = kwargs["python_version"]
        super(PythonJob, self).__init__(*args, **kwargs)

        self["name"] = "jenkins-manager__python-{{python_version}}__{{type}}__{{git_branch}}"
        self["display-name"] = "jenkins-manager python{{python_version}} {{type}}__{{git_branch}}"

        self.builders = [
            {"shining-panda": {
                "build-environment": "virtualenv",
                "python-version": self.version_string_map[python_version],
                "nature": "shell",
                "command": """#!/usr/bin/env bash
set -x
set -e
echo "==========================================="
python --version
echo "==========================================="
echo
{{command}}
                """
            }}]


class PythonUnitTestJob(PythonJob):
    def __init__(self, *args, **kwargs):
        super(PythonUnitTestJob, self).__init__(type="unit", *args, **kwargs)

        self["command"] = """
echo "Installing Python testing requirements"
pip install -r requirements-test.txt

echo "Installing Jenkins Job Builder 2.x"
git clone -b jjb-2.0.0-api https://github.com/waynr/jenkins-job-builder
pip install -e ./jenkins-job-builder

echo "Installing Jenkins Manager"
pip install -e ./

echo "Actually run the tests..."
python setup.py testr --slowest
        """


class JenkinsManagerPipeline(pipeline.TriggerParameterizedBuildPipeline):

    def __init__(self, python_version_list=None, *args, **kwargs):
        if python_version_list is None:
            python_version_list = ["2.7"]

        jobs = []
        for version in python_version_list:
            jobs.append(PythonUnitTestJob(python_version=version))

        lint = PythonJob(type='lint',
                         command="""
echo "Installing Python testing requirements"
pip install -r requirements-test.txt

python setup.py testr --slowest
        """)

        jobs.insert(0, lint)

        for j in jobs:
            self.append(j)

        self.render(kwargs)


def get_jobs():

    pipe1 = JenkinsManagerPipeline(
        python_version_list=[
            "2.7", "3.4"
        ],
        git_branch="master"
    )

    pipe2 = JenkinsManagerPipeline(
        python_version_list=[
            "2.7", "3.4"
        ],
        git_branch="tutorial"
    )

    pipe1.extend(pipe2)

    return pipe1
