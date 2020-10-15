def test_iterate(config):
    assert len(config) == 10
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
