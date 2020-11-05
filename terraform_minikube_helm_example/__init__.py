# Support Invoke discovery of tasks
from .tasks import *

# Collection configured for expected use
from invoke import Collection

ns = Collection()

ns.add_task(create)
ns.add_task(destroy)

ns.configure({
    'terraform_minikube_helm_example': {
        'working_dir': 'terraform_minikube_helm_example',
        'bin_dir': '../bin',
        'helm_charts_dir': '../helm',
    }
})

try:
    from . import instance_1 as instance_1
    ns.add_collection(instance_1.ns, name='instance_1')
    ns.configure({
        'terraform_minikube_helm_example': instance_1.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass

try:
    from . import instance_2 as instance_2
    ns.add_collection(instance_2.ns, name='instance_2')
    ns.configure({
        'terraform_minikube_helm_example': instance_2.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass

del Collection
