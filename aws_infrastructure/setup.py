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
        'boto3>=1,<2',
        'colorama>=0.4.4,<0.5',
        'invoke>=1,<2',
        'paramiko>=2,<3',
        'ruamel.yaml>=0.17,<0.18',
        'semver>=2,<3'
    ],
)
