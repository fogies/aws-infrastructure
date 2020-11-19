from invoke import Collection

from .tasks import *

# Collection configured for expected use
ns = Collection()

ns.add_task(apply)
ns.add_task(destroy)

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'terraform_minikube_helm_example',
        'bin_dir': '../bin',
        'helm_charts_dir': '../helm',
    }
})

del Collection

try:
    from . import instance_1 as instance_1
    ns.add_collection(instance_1.ns, name='instance_1')
    ns.configure({
        CONFIG_KEY: instance_1.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass

try:
    from . import instance_2 as instance_2
    ns.add_collection(instance_2.ns, name='instance_2')
    ns.configure({
        CONFIG_KEY: instance_2.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass
