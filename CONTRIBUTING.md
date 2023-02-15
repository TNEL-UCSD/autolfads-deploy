# Contributing Guidelines

Thank you for your interest in contributing to `autolfads-deploy`! We welcome all contributions to the project that extend or improve code and/or documentation. This page includes information and guidelines for how to get involved and contribute to the project.

This project adheres to a [code of conduct](github.com/TNEL-UCSD/autolfads-deploy/blob/master/CODE_OF_CONDUCT.md) that you are expected to uphold when participating in this project.

On this page, you can find information on:

* [Reporting a problem](#reporting-a-problem)
* [Getting involved in the project](#getting-involved)
* [Project scope](#project-scope)
* [Making a contribution](#making-a-contribution)
* [Project conventions](#project-conventions)

## Reporting a Problem

To report an issue with the code, please submit it to our [issue tracker](https://github.com/TNEL-UCSD/autolfads-deploy/issues).

In doing so, please try to include the following:

1. A short, top-level summary of the issue (usually 1-2 sentences)
2. A short, self-contained code snippet to reproduce the issue, ideally allowing a simple copy and paste to reproduce
3. The observed outcome of the code snippet
4. The expected outcome of the code snippet

## Getting Involved

We welcome all kinds of contributions to the project, including suggested features and help with documentation, maintenance, and updates.

If you have a new idea you would like to suggest or contribute, please do the following:

1. Check if the idea is already being discussed on the [issues](https://github.com/TNEL-UCSD/autolfads-deploy/issues) page
2. Check that your idea is within the [project scope](#project-scope)
3. Open an [issue](https://github.com/TNEL-UCSD/autolfads-deploy/issues) describing what you would like to see added / changed, and why
4. Indicate in the issue if the idea is something you would be willing to help implement
5. If you want to work on the contribution, follow the [contribution guidelines](#making-a-contribution)

If you are interested in getting involved and helping with the project, a great place to start is to visit the [issues](https://github.com/fooof-tools/fooof/issues) page and see if there is anything you would be interested in helping with. If so, join the conversation, and project developers can help get you started.

## Project Scope

`autolfads-deploy` is a repository that provides a set of solutions for running AutoLFADS in different compute environments and workflows. Code and documentation that targets maintaining Kubernetes or bare metal machines will most likely be considered out of scope. Additionally, AutoLFADS algorithmic changes might be more suitable for that [repository](https://github.com/snel-repo/autolfads-tf2).

## Making a Contribution

If there is a feature you would like to add, or an issue you saw that you think you can help with, you are ready to make a submission to the project!

If you are working on a feature, please indicate so in the relevant issue, so that we can keep track of who is working on what.

Once you're ready to start working on your contribution, do the following:

1. [Fork this repository](https://help.github.com/articles/fork-a-repo/), which makes your own version of this project you can edit
2. [Make your changes](https://guides.github.com/activities/forking/#making-changes), updating or adding code to add the desired functionality
3. [Check the project conventions](#project-conventions), and make sure all new or updated code follows the guidelines
4. [Submit a pull request](https://help.github.com/articles/proposing-changes-to-a-project-with-pull-requests/), to start the process of merging the new code to the primary branch


## Project Conventions

All code contributed to the module should follow these conventions:

1. Code Requirements
    * All code should be written in Python, golang (Kubeflow components only), or shell, and run on the minimum Kubeflow required version that is noted in the README
    * New dependencies should be avoided if possible, especially if they are not in PyPI or Anaconda
    * If any new dependencies are needed, they should be added to the `requirements.txt` file

2. Code Style
    * Code should generally follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guidelines
    * Max line length is 100 characters
    * Merge candidates will be checked using [pylint](https://www.pylint.org)

3. API & Naming Conventions
    * Try to keep the API consistent with existing code in terms of parameter names and ordering
    * Use standard casing, for example:
         * function names should be in snake_case (all lowercase with underscores)
         * class names should be in CamelCase (leading capitals with no separation)

4. Code Documentation
    * All code should be documented, including in-code comments describing procedures, and detailed docstrings
    * Docstrings should follow the [numpy docs](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) format
        * At minimum, there should be a sentence describing what the function does and a list of parameters and returns
        * Private functions should be indicated with a leading underscore, and should still include a docstring including at least a sentence describing what the function does
    * If possible, add an `Examples` section to the docstrings, that demonstrates a simple use case
        * If so, these examples should be executable, using [doctest](https://docs.python.org/3/library/doctest.html)
        * If examples cannot be run, use the SKIP directive

5. Code Tests
    * This project uses the [pytest](https://docs.pytest.org/en/latest/) testing tool for testing module code
    * All new code requires test code, written as unit tests that check each function and class in the module
    * Tests should be, at a minimum, 'smoke tests' that execute the code and check that it runs without raising an error
        * Where possible, accuracy checking is encouraged, though not strictly required
    * Merge candidates must pass all existing tests, and add new tests such as to not reduce test coverage
    * To run the tests locally, pytest needs to be installed (`pip install pytest`)
        * To run the tests on a local copy of the module, move into the folder and run `pytest .`


For more guidelines on how to write well formated and organized code, check out the [Python API Checklist](http://python.apichecklist.com).
