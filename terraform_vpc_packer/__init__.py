# Support Invoke discovery of tasks
from .tasks import *

# Collection configured for expected use
from invoke import Collection

ns = Collection()

ns.add_task(create)
ns.add_task(destroy)

ns.configure({
    'working_dir': 'terraform_vpc_packer',
    'bin_dir': '../bin'
})

del Collection
