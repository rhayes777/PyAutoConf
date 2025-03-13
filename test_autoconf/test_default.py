from autoconf.mock.mock_real import Redshift


def test_override_file(config):
    hpc = config["general"]["hpc"]

    assert hpc["hpc_mode"] is False
    assert hpc["default_field"] == "hello"


def test_logging_config(config, files_directory):
    assert config.logging_config["name"] == "config"

    config.push(files_directory / "default")
    assert config.logging_config["name"] == "default"


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
    config.push(files_directory / "default", keep_first=True)

    assert config["general"]["hpc"]["hpc_mode"] is False


def test_override_in_directory(config):
    superscript = config["text"]["label"]["superscript"]

    assert superscript["Galaxy"] == "g"
    assert superscript["default_field"] == "label default"


def test_novel_directory(config):
    assert config["default"]["other"]["section"]["key"] == "value"


def test_novel_file(config):
    assert config["default_file"]["section"]["key"] == "file value"


def test_json(config):
    assert (
        config.prior_config.for_class_and_suffix_path(Redshift, ["redshift"])[
            "upper_limit"
        ]
        == 3.0
    )
    assert (
        config.prior_config.for_class_and_suffix_path(Redshift, ["rodshift"])[
            "upper_limit"
        ]
        == 4.0
    )


def test_embedded_yaml_default(config):
    embedded_dict = config["embedded"]["first"]["first_a"]

    assert embedded_dict["first_a_a"] == "one"
    assert embedded_dict["first_a_b"] == "two"
    assert embedded_dict["first_a_c"] == "three"


def test_as_dict(config):
    embedded_dict = config["embedded"]["first"]["first_a"]

    assert {**embedded_dict}


def test_mix_files(config):
    embedded_dict = config["one"]["two"]["three"]

    assert embedded_dict["four"] == "five"
    assert embedded_dict["six"] == "seven"
    assert embedded_dict["eight"] == "nine"
