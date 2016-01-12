import jenkins_manager.types.job as job
import jenkins_manager.types.pipeline as pipeline


class BaseJob(job.TemplateJob):

    def __init__(self, *args, **kwargs):
        super(BaseJob, self).__init__(*args, **kwargs)
        self["name"] = "jenkins-manager__{{language}}__{{type}}"
        self["display-name"] = "jenkins-manager {{language}} {{type}}"

        self["scm"] = [{
            "git": {
                "url": "https://github.com/waynr/jenkins-manager",
                "skip-tag": True,
                "branches": [
                    "master",
                ],
            },
        }]

        self.update(kwargs)


class PythonJob(BaseJob):

    def __init__(self, *args, **kwargs):
        super(PythonJob, self).__init__(language="python", *args, **kwargs)

        self.builders = [
            {"shining-panda": {
                "build-environment": "virtualenv",
                "python-version": "System-CPython-2.7",
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


class JenkinsManagerPipeline(pipeline.TriggerParameterizedBuildPipeline):

    def __init__(self, *args, **kwargs):
        test = PythonJob(type='unit',
                         command="""
echo "Installing Python testing requirements"
pip install -r requirements-test.txt

echo "Installing Jenkins Job Builder 2.x"
git clone -b jjb-2.0.0-api https://github.com/waynr/jenkins-job-builder
pip install -e ./jenkins-job-builder

echo "Installing Jenkins Manager"
pip install -e ./

echo "Actually run the tests..."
python setup.py testr --slowest
        """)

        lint = PythonJob(type='lint',
                         command="""
echo "Installing Python testing requirements"
pip install -r requirements-test.txt

python setup.py testr --slowest
        """)

        for j in lint, test:
            self.append(j)

        self.render()


def get_jobs():

    pipe1 = JenkinsManagerPipeline()

    return pipe1
