def test_iterate_directory(config):
    keys = {item[0] for item in config}
    assert keys == {
        'default',
        'default_file',
        'general',
        'json_priors',
        'label',
        'label_format',
        'non_linear',
        'priors',
        'text',
        'visualize'
    }


def test_iterate_file(config):
    keys = {item[0] for item in config["general"]}
    assert keys == {'hpc', 'fits', 'output'}


def test_iterate_section(config):
    keys = {item[0] for item in config["general"]["hpc"]}
    assert keys == {'iterations_per_update', 'default_field', 'hpc_mode'}


def test_override(config):
    assert dict(config["general"]["hpc"])["hpc_mode"] is False
