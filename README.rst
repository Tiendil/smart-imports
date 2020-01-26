
#######################
Smart import for Python
#######################

|pypi| |python_versions| |test_coverege_develop|

Automatically discovers & imports entities, used in current module.

No magic or monkey patching. Only standard Python functionality.

+---------------------------------------------+---------------------------------------------+
| Before                                      | After                                       |
+=============================================+=============================================+
|.. code:: python                             |.. code:: python                             |
|                                             |                                             |
|    import math                              |    import smart_imports                     |
|    from my_project import calc              |    smart_imports.all()                      |
|    # 100500 other imports                   |    # no any other imports                   |
|                                             |                                             |
|    def my_code(argument, function=calc):    |    def my_code(argument, function=calc):    |
|        return math.log(function(argument))  |        return math.log(function(argument))  |
|                                             |                                             |
+---------------------------------------------+---------------------------------------------+

-------------
Short summary
-------------

* Get source code of module, from which ``smart_imports`` has called;
* Parse it, find all not initialized variables;
* Search imports, suitable for found variables;
* Import them.

Process only modules, from which ``smart_imports`` called explicitly.

--------
See also
--------

- `Gitter chat room <https://gitter.im/smart-imports/discussion>`_
- `Change log <https://github.com/Tiendil/smart-imports/blob/develop/CHANGELOG.rst>`_


.. |pypi| image:: https://img.shields.io/pypi/v/smart_imports.svg?style=flat-square&label=latest%20stable%20version&reset_github_caches=5
    :target: https://pypi.python.org/pypi/smart_imports
    :alt: Latest version released on PyPi

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/smart_imports.svg?style=flat-square&reset_github_caches=5
    :target: https://pypi.python.org/pypi/smart_imports
    :alt: Supported Python versions

.. |test_coverege_develop| image:: https://coveralls.io/repos/github/Tiendil/smart-imports/badge.svg?branch=develop&reset_github_caches=5
    :target: https://coveralls.io/github/Tiendil/smart-imports?branch=develop
    :alt: Test coverage in develop
