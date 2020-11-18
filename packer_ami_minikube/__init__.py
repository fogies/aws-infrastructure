from invoke import Collection

from .tasks import *

# Collection configured for expected use
ns = Collection()

ns.add_task(build)

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'packer_ami_minikube',
        'bin_dir': '../bin'
    }
})

del Collection
