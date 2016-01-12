import jenkins_manager.types.job as job


class BaseJob(job.Job):

    def __init__(self, *args, **kwargs):
        super(BaseJob, self).__init__(*args, **kwargs)


def get_jobs():

    job1 = BaseJob({
        "name": "jenkins-manager",
        "display-name": "jenkins-manager Noop Job",
    })

    return [job1]
