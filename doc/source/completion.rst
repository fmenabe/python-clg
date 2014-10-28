**********
Completion
**********

.. code-block:: python

    >>> import clg
    >>> import yaml
    >>> import yamlorderdeddictloader
    >>> cmd = clg.CommandLine(yaml.load(open('cmd.yml'),
                              Loader=yamlordereddictloader.Loader))
    >>> with open('/etc/bash_completion.d/myprog') as fhandler:
    >>>     fhandler.write(cmd.gen_bash_completion())
