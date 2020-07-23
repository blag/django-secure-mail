import sys
from shutil import rmtree
from setuptools import setup, find_packages


if sys.argv[:2] == ["setup.py", "bdist_wheel"]:
    # Remove previous build dir when creating a wheel build,
    # since if files have been removed from the project,
    # they'll still be cached in the build dir and end up
    # as part of the build, which is unexpected.
    try:
        rmtree("build")
    except Exception:
        pass


setup(
    name="django-secure-mail",
    version=__import__("secure_mail").__version__,
    author="blag",
    author_email="blag@users.noreply.github.com",
    description="A Django reusable app providing the ability to send PGP "
                "encrypted and multipart emails using the Django templating "
                "system.",
    long_description=open("README.rst").read(),
    long_description_content_type='text/x-rst',
    url="https://github.com/blag/django-secure-mail",
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "django",
        "python-gnupg",
    ],
    extras_require={
        'dev': [
            "check-manifest",
            "sphinx-me",
            "twine",
        ],
        'test': [
            "coverage",
            "flake8",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
        "Topic :: Communications :: Email",
        "Topic :: Security :: Cryptography",
    ]
)
