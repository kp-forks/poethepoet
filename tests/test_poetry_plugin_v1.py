import os
import re

import pytest


@pytest.fixture(scope="module")
def _setup_poetry_project(run_poetry_1, projects):
    run_poetry_1(["install"], cwd=projects["poetry_plugin"])


@pytest.fixture(scope="module")
def _setup_poetry_project_empty_prefix(run_poetry_1, projects):
    run_poetry_1(
        ["install"],
        cwd=projects["poetry_plugin/empty_prefix"].parent,
    )


@pytest.fixture(scope="module")
def _setup_poetry_project_with_prefix(run_poetry_1, projects):
    run_poetry_1(
        ["install"],
        cwd=projects["poetry_plugin/with_prefix"].parent,
    )


@pytest.mark.slow
def test_poetry_help(run_poetry_1, projects):
    result = run_poetry_1([], cwd=projects["poetry_plugin"])
    assert result.stdout.startswith("Poetry (version ")
    assert "poe cow-greet" in result.stdout
    assert re.search(r"\n  poe echo\s+It's like echo\n", result.stdout)


# TODO: re-enable this test
@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS", "false") == "true",
    reason="Skipping test the doesn't seem to work in GitHub Actions lately",
)
@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_task_with_cli_dependency(run_poetry_1, projects, is_windows):
    result = run_poetry_1(
        ["poe", "cow-greet", "yo yo yo"],
        cwd=projects["poetry_plugin"],
    )
    if is_windows:
        assert result.stdout.startswith("Poe => cowpy 'yo yo yo'")
        assert "< yo yo yo >" in result.stdout
    else:
        # On POSIX cowpy expects notices its being called as a subprocess and tries
        # unproductively to take input from stdin
        assert result.stdout.startswith("Poe => cowpy 'yo yo yo'")
        assert (
            "< Cowacter, eyes:default, tongue:False, thoughts:False >" in result.stdout
        )


# TODO: re-enable this test
@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS", "false") == "true",
    reason="Skipping test the doesn't seem to work in GitHub Actions lately",
)
@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_task_with_lib_dependency(run_poetry_1, projects):
    result = run_poetry_1(["poe", "cow-cheese"], cwd=projects["poetry_plugin"])
    assert result.stdout == (
        "Poe => from cowpy import cow; print(list(cow.COWACTERS)[5])\ncheese\n"
    )


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_task_accepts_any_args(run_poetry_1, projects):
    result = run_poetry_1(
        ["poe", "echo", "--lol=:D", "--version", "--help"],
        cwd=projects["poetry_plugin"],
    )
    assert result.stdout == (
        "Poe => poe_test_echo --lol=:D --version --help\n--lol=:D --version --help\n"
    )


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_empty_prefix")
def test_poetry_help_without_poe_command_prefix(run_poetry_1, projects):
    result = run_poetry_1([], cwd=projects["poetry_plugin/empty_prefix"].parent)
    assert result.stdout.startswith("Poetry (version ")
    assert "\n  cow-greet" in result.stdout
    assert "\n  echo               It's like echo\n" in result.stdout


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_empty_prefix")
def test_running_tasks_without_poe_command_prefix(run_poetry_1, projects):
    result = run_poetry_1(
        ["echo", "--lol=:D", "--version", "--help"],
        cwd=projects["poetry_plugin/empty_prefix"].parent,
    )
    assert result.stdout == (
        "Poe => poe_test_echo --lol=:D --version --help\n--lol=:D --version --help\n"
    )


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_empty_prefix")
def test_poetry_command_from_included_file_with_empty_prefix(run_poetry_1, projects):
    result = run_poetry_1(
        ["included-greeting"],
        cwd=projects["poetry_plugin/empty_prefix"].parent,
    )
    assert result.stdout.startswith("Poe => echo 'Greetings from another file!'")


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_empty_prefix")
def test_poetry_help_with_poe_command_prefix(run_poetry_1, projects):
    result = run_poetry_1([], cwd=projects["poetry_plugin/with_prefix"].parent)
    assert result.stdout.startswith("Poetry (version ")
    assert "\n  foo cow-greet" in result.stdout
    assert "\n  foo echo           It's like echo\n" in result.stdout
    assert "_secret_task" not in result.stdout


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_with_prefix")
def test_running_tasks_with_poe_command_prefix(run_poetry_1, projects):
    result = run_poetry_1(
        ["foo", "echo", "--lol=:D", "--version", "--help"],
        cwd=projects["poetry_plugin/with_prefix"].parent,
    )
    assert result.stdout == (
        "Poe => poe_test_echo --lol=:D --version --help\n--lol=:D --version --help\n"
    )


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project_with_prefix")
def test_running_tasks_with_poe_command_prefix_missing_args(run_poetry_1, projects):
    result = run_poetry_1(
        ["foo"],
        cwd=projects["poetry_plugin/with_prefix"].parent,
    )
    assert "Usage:\n  poetry foo [global options]" in result.stdout


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_running_poetry_command_with_hooks(run_poetry_1, projects):
    result = run_poetry_1(["env", "info"], cwd=projects["poetry_plugin"])
    assert "THIS IS YOUR ENV!" in result.stdout
    assert "THAT WAS YOUR ENV!" in result.stdout


@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_running_poetry_command_with_hooks_with_directory(run_poetry_1, projects):
    result = run_poetry_1(
        ["--directory=" + str(projects["poetry_plugin"]), "env", "info"],
        cwd=projects["poetry_plugin"].parent,
    )
    assert "THIS IS YOUR ENV!" in result.stdout
    assert "THAT WAS YOUR ENV!" in result.stdout


# TODO: re-enable this test
@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS", "false") == "true",
    reason="Skipping test the doesn't seem to work in GitHub Actions lately",
)
@pytest.mark.slow
@pytest.mark.usefixtures("_setup_poetry_project")
def test_task_with_cli_dependency_with_directory(run_poetry_1, projects, is_windows):
    result = run_poetry_1(
        [
            "--directory=" + str(projects["poetry_plugin"]),
            "poe",
            "cow-greet",
            "yo yo yo",
        ],
        cwd=projects["poetry_plugin"].parent,
    )
    if is_windows:
        assert result.stdout.startswith("Poe => cowpy 'yo yo yo'")
        assert "< yo yo yo >" in result.stdout
    else:
        # On POSIX cowpy expects notices its being called as a subprocess and tries
        # unproductively to take input from stdin
        assert result.stdout.startswith("Poe => cowpy 'yo yo yo'")
        assert (
            "< Cowacter, eyes:default, tongue:False, thoughts:False >" in result.stdout
        )
