import datetime
import setuptools

build_time = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

setuptools.setup(
    name='aws_infrastructure',
    version='0.1.0.{}'.format(build_time),
    # author='',
    # author_email='',
    packages=setuptools.find_packages(),
    scripts=[
    ],
    url='https://github.com/fogies/aws-infrastructure',
    # license='',
    # description='',
    # long_description='',
    install_requires=[
    ],
)
