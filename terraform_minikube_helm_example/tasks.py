from invoke import task
import os
import aws_infrastructure.task_templates


CONFIG_KEY = 'terraform_minikube_helm_example'


@task
def delete_empty_instance_dirs(context):
    """
    Delete any instance directories which are empty.
    """

    config = context.config[CONFIG_KEY]
    working_dir = os.path.normpath(config.working_dir)

    # Terraform will create but not automatically remove instance directories
    # If any instance directories are now empty, delete them
    list_instance_dir = ['instance_1', 'instance_2']
    for instance_dir_current in list_instance_dir:
        instance_dir_path = os.path.normpath(os.path.join(working_dir, instance_dir_current))
        if os.path.isdir(instance_dir_path):
            # Some files may exist and need to be deleted
            delete_known_files = [
                'known_hosts',  # Created as part of SSH access
            ]

            # Determine if all existing files are known
            existing_files = os.listdir(instance_dir_path)
            unknown_files = list(set(existing_files) - set(delete_known_files))

            # If we can delete everything, do it, otherwise leave everything
            if len(unknown_files) == 0:
                for file_current in existing_files:
                    os.remove(os.path.normpath(os.path.join(instance_dir_path, file_current)))
                os.rmdir(instance_dir_path)


init = aws_infrastructure.task_templates.terraform.task_init(
    config_key=CONFIG_KEY
)
apply = aws_infrastructure.task_templates.terraform.task_apply(
    config_key=CONFIG_KEY,
    init=init,
    post=[delete_empty_instance_dirs]
)
destroy = aws_infrastructure.task_templates.terraform.task_destroy(
    config_key=CONFIG_KEY,
    init=init,
    post=[delete_empty_instance_dirs]
)
