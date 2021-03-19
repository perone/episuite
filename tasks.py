from invoke import task


@task
def test(c, slow=True):
    if slow:
        c.run("python -m pytest --cov=episuite tests/")
    else:
        c.run("python -m pytest --cov=episuite -m 'not slow' tests/")

@task
def lint(c, docstyle=False):
    print("Running flake8...")
    c.run("flake8 --show-source --statistics episuite")
    print("Running mypy...")
    c.run('mypy episuite')
    print("Running isort...")
    c.run('isort -c .')
    if docstyle:
        print("Running pydocstyle...")
        c.run('pydocstyle episuite')


@task
def lint_fix(c):
    c.run('isort episuite tests')


@task
def watch_docs(c):
    c.run("sphinx-autobuild docs/source docs/build")


@task
def make_docs(c):
    c.run("cd docs; make html")
