from autoconf.mock.mock_real import Redshift


def test_override_file(config):
    hpc = config["general"]["hpc"]

    assert hpc["hpc_mode"] is False
    assert hpc["default_field"] == "hello"


def test_push(config, files_directory):
    assert len(config.configs) == 2
    assert config["general"]["hpc"]["hpc_mode"] is False

    config.push(files_directory / "default")

    assert len(config.configs) == 2
    assert config["general"]["hpc"]["hpc_mode"] is True

    config.push(files_directory / "config")

    assert len(config.configs) == 2
    assert config["general"]["hpc"]["hpc_mode"] is False


def test_keep_first(config, files_directory):
    config.push(
        files_directory / "default",
        keep_first=True
    )

    assert config["general"]["hpc"]["hpc_mode"] is False


def test_override_in_directory(config):
    subscript = config["text"]["label"]["subscript"]

    assert subscript["Galaxy"] == "g"
    assert subscript["default_field"] == "label default"


def test_novel_directory(config):
    assert config["default"]["other"]["section"]["key"] == "value"


def test_novel_file(config):
    assert config["default_file"]["section"]["key"] == "file value"


def test_json(config):
    assert config.prior_config.for_class_and_suffix_path(
        Redshift, ["redshift"]
    )["upper_limit"] == 3.0
    assert config.prior_config.for_class_and_suffix_path(
        Redshift, ["rodshift"]
    )["upper_limit"] == 4.0