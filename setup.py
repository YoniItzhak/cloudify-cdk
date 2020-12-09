from os import path

from setuptools import setup


def get_readme_contents():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md')) as f:
        return f.read()


setup(
    name='cloudify-cdk',
    long_description=get_readme_contents(),
    long_description_content_type='text/markdown',
    version='1.0.0',
    author='Cloudify',
    author_email='cosmo-admin@cloudify.co',
    packages=['cloudify_cdk'],
    include_package_data=True,
    license='LICENSE',
    description="Cloudify Cloud Development Kit",
    entry_points={
        'console_scripts': [
            'cfycdk = cloudify_cdk.main:main'
        ]
    },
    install_requires=[
        'pyyaml>=5.3.0,<5.4.0',
        'jinja2>=2.11.0,<2.12.0',
    ]
)
