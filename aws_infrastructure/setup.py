import setuptools

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
        'boto3',
        'colorama',
        'invoke',
        'paramiko',
        'pipenv',
        'python-dotenv',
        'ruamel.yaml',
        'semver'
    ],
)
