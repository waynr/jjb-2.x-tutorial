import jenkins_manager.types.job as job


class BaseJob(job.TemplateJob):

    def __init__(self, *args, **kwargs):
        super(BaseJob, self).__init__(*args, **kwargs)
        self["name"] = "jenkins-manager__{{type}}"
        self["display-name"] = "jenkins-manager {{type}}"

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


def get_jobs():

    job1 = BaseJob(type='unit')
    job1.builders = [
        {"shell": """#!/usr/bin/env bash
set -e
set -x

echo "Setting up and activating virtualenv"
virtualenv .virtualenv && source .virtualenv/bin/activate

echo "Installing Python testing requirements"
pip install -r requirements-test.txt

echo "Installing Jenkins Job Builder 2.x"
git clone -b jjb-2.0.0-api https://github.com/waynr/jenkins-job-builder
pip install -e ./jenkins-job-builder

echo "Installing Jenkins Manager"
pip install -e ./

echo "Actually run the tests..."
python setup.py testr --slowest
        """},
    ]

    job2 = BaseJob(type='lint')
    job2.builders = [
        {"shell": """#!/usr/bin/env bash
set -e
set -x

echo "Setting up and activating virtualenv"
virtualenv .virtualenv && source .virtualenv/bin/activate

echo "Installing Python testing requirements"
pip install -r requirements-test.txt

python setup.py testr --slowest
        """},
    ]

    return [job1, job2]
