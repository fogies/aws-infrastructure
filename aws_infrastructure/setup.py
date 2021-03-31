import datetime
import setuptools

# Semantic Versioning does not allow leading zeroes in dot-separated identifiers,
# this datetime format will increment but is intentionally not dot-separated
build_time = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

setuptools.setup(
    name='aws_infrastructure',
    # Should follow Semantic Versioning <https://semver.org/>
    version='0.1.0-dev{}'.format(build_time),
    # author='',
    # author_email='',
    packages=setuptools.find_packages(),
    url='https://github.com/fogies/aws-infrastructure',
    # license='',
    # description='',
    # long_description='',
    python_requires='>=3',
    install_requires=[
        'invoke>=1.5',
        'paramiko>=2.7.2',
        'ruamel.yaml>=.17,<.18',
        'semver>=3.0.0.dev2'
    ],
)
