import datetime
import setuptools

# Semantic Versioning does not allow leading zeroes in dot-separated identifiers,
# this datetime format will increment but is intentionally not dot-separated
build_time = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

setuptools.setup(
    name='aws_infrastructure',
    # Should follow Semantic Versioning <https://semver.org/>
    version='0.0.1',
    # author='',
    # author_email='',
    packages=setuptools.find_packages(),
    url='https://github.com/fogies/aws-infrastructure',
    # license='',
    # description='',
    # long_description='',
    python_requires='>=3',
    install_requires=[
        'boto3>=1,<2',
        'invoke>=1,<2',
        'paramiko>=2,<3',
        'ruamel.yaml>=0.17,<0.18',
        'semver>=2,<3'
    ],
)
