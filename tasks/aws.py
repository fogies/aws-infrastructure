from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.aws_configure
from invoke import Collection

CONFIG_KEY = 'aws'
AWS_ENV_PATH = './secrets/aws/.aws_env'
AWS_CONFIGS = {
    'probe': aws_infrastructure.tasks.library.aws_configure.AWSConfig(
        aws_config_path='./secrets/aws/aws-infrastructure.config',
        profile='probe',
    ),
    'uwscope': aws_infrastructure.tasks.library.aws_configure.AWSConfig(
        aws_config_path='./secrets/aws/aws-infrastructure.config',
        profile='uwscope',
    ),
}

ns = Collection('aws')

ns_configure = aws_infrastructure.tasks.library.aws_configure.create_tasks(
    config_key=CONFIG_KEY,
    aws_env_path=AWS_ENV_PATH,
    aws_configs=AWS_CONFIGS,
)

compose_collection(
    ns,
    ns_configure,
)
