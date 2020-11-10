# Support Invoke discovery of tasks
from .tasks import *

# Collection configured for expected use
from invoke import Collection

ns = Collection()

ns.add_task(build)

ns.configure({
    'packer_ami_minikube': {
        'working_dir': 'packer_ami_minikube',
        'bin_dir': '../bin'
    }
})

del Collection
