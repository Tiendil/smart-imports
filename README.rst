
=========================
 Smart import for Python
=========================

|pypi| |python_versions| |test_coverege_develop|

- `Gitter chat room <https://gitter.im/smart-imports/discussion>`_
- `Changelog <https://github.com/Tiendil/smart-imports/blob/develop/CHANGELOG.rst>`_

Automatically discovers & imports entities, used in the current module.

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

`MyPy`_ supported.

Summary
=======

* Get source code of the module, from which ``smart_imports.all()`` has called.
* Parse it, find all not initialized variables.
* Search imports, suitable for found variables.
* Import them.

Library process only modules, from which ``smart_imports`` called explicitly.

Main idea
=========

With time every complex project develops own naming convention. If we translate that convention into more formal rules, we will be able to make automatic imports of every entity, knowing only its name.

For example, we will not need to write ``import math`` to call ``math.pi``, since our system will understand that ``math`` is the module of the standard library.

How it works
============

Code from the header works in such way:

- ``smart_imports.all()`` builds `AST <https://en.wikipedia.org/wiki/Abstract_syntax_tree>`_ of the module from which it has called.
- Library analyses AST and searches for not initialized variables.
- Name of every found variable processed thought chain of rules to determine the correct module (or its attribute) to import. If the rule finds the target module, chain breaks and the next rules will not be processed.
- Library load found modules and add imported entities into the global namespace.

``Smart Imports`` searches not initialized variables in every part of code (including new Python syntax).

Automatic importing turns on only for modules, that do explicit call of ``smart_imports.all()``.

Moreover, you can use normal imports with ``Smart Imports`` at the same time. That helps to integrate ``Smart Imports`` step by step.

You can notice, that AST of module builts two times:

- when CPython imports module;
- when ``Smart Imports`` process call of ``smart_imports.all()``.

We can build AST once (for that we can add hook into the process of importing modules with help of `PEP-0302 <https://www.python.org/dev/peps/pep-0302/>`_), but it will make import event slower. I think that it is because at import time CPython builds AST in terms of its internal structures (probably implemented in C). Conversion from them to Python AST cost more than building new AST from scratch.

``Smart Imports`` build AST only once for every module.

Default import rules
====================

``Smart Imports`` can be used without configuration. By default it uses such rules:

#. By exact match looks for the module with the required name in the folder of the current module.
#. Checks if the standard library has a module with the required name.

   #. By exact match with top-level packages (for example, ``math`` ).
   #. For sub-packages and modules checks complex names with dots replaced by underscores (for example, ``os.path`` will be imported for name ``os_path``).

#. By exact match looks for installed packages with the required name (for example, ``requests`` ).

Performance
===========

``Smart Imports`` does not slow down runtime but increases startup time.

Because of building AST, startup time increased in 1.5-2 times. For small projects it is inconsequential. At the same time, the startup time of large projects depends mostly on architecture and dependencies between modules, than from the time of modules import.

In the future, part of ``Smart Imports`` can be rewritten in C — it should eliminate startup delays.

To speed up startup time, results of AST processing can be cached on the file system. That behavior can be turned on in the config. ``SmartImports`` invalidates cache when module source code changes.

Also, ``Smart Imports``' work time highly depends on rules and their sequence. You can reduce these costs by modifying configs. For example, you can specify an explicit import path for a name with `Rule 4: custom names`_.

Configuration
=============

The logic of default configuration was already described. It should be enough to work with the standard library.

Default config:

.. code-block:: javascript

    {
        "cache_dir": null,
        "rules": [{"type": "rule_local_modules"},
                  {"type": "rule_stdlib"},
                  {"type": "rule_predefined_names"},
                  {"type": "rule_global_modules"}]
    }


If necessary, a more complex config can be put on a file system.

`Example of complex config <https://github.com/the-tale/the-tale/blob/develop/src/the_tale/the_tale/smart_imports.json>`_ (from my pet project).

At the time of call ``smart_import.all()`` library detects a location of config file by searching file ``smart_imports.json`` from the current folder up to root. If a file will be found, it will become config for the current module.

You can use multiple config files (place them in different folders).

There are few config parameters now:

.. code-block:: javascript

    {
        // folder to store cached AST
        // if not specified or null, cache will not be used
        "cache_dir": null|"string",

        // list of import rules (see further)
        "rules": []
    }

Import rules
============

A sequence of rules in configs determines the order of their application. The first success rule stops processing and makes import.

`Rule 1: predefined names`_ will be often used in the examples below. It required for the correct processing of default names like ``print``.

Rule 1: predefined names
------------------------

Rule silences import search for predefined names like ``__file__`` and builtins like ``print``.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"}]
    # }

    import smart_imports

    smart_imports.all()

    # Smart Imports will not search for module with name __file__
    # event if variable is not initialized explicity in code
    print(__file__)


Rule 2: local modules
---------------------

Rule checks if a module with the required name exists in the folder of the current module. If the module found, it will be imported.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_local_modules"}]
    # }
    #
    # project on file sytem:
    #
    # my_package
    # |-- __init__.py
    # |-- a.py
    # |-- b.py

    # b.py
    import smart_imports

    smart_imports.all()

    # module "a" will be found and imported
    print(a)


Rule 3: global modules
----------------------

Rule tries to import the module by name.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_global_modules"}]
    # }
    #
    # install external package
    #
    # pip install requests

    import smart_imports

    smart_imports.all()

    # module "requests" will be found and imported
    print(requests.get('http://example.com'))


Rule 4: custom names
--------------------

Rule links a name to the specified module and its attribute (optionally).

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_custom",
    #               "variables": {"my_import_module": {"module": "os.path"},
    #                             "my_import_attribute": {"module": "random", "attribute": "seed"}}}]
    # }

    import smart_imports

    smart_imports.all()

    # we use modules of the standard library in that example
    # but any module can be used
    print(my_import_module)
    print(my_import_attribute)


Rule 5: standard library
------------------------

Rule checks if the standard library has a module with the required name. For example ``math`` or ``os.path`` (which will be imported for the name ``os_path``).

That rule works faster than `Rule 3: global modules`_, since it searches module by predefined list. Lists of modules for every Python version was collected with help of `stdlib-list <https://pypi.org/project/stdlib-list/>`_.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_stdlib"}]
    # }

    import smart_imports

    smart_imports.all()

    print(math.pi)


Rule 6: import by prefix
------------------------

Rule imports module by name from the package, which associated with name prefix. It can be helpful when you have a package used in the whole project. For example, you can access modules from package ``utils`` with prefix ``utils_``.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_prefix",
    #               "prefixes": [{"prefix": "utils_", "module": "my_package.utils"}]}]
    # }
    #
    # project on filesystem
    #
    # my_package
    # |-- __init__.py
    # |-- utils
    # |-- |-- __init__.py
    # |-- |-- a.py
    # |-- |-- b.py
    # |-- subpackage
    # |-- |-- __init__.py
    # |-- |-- c.py

    # c.py

    import smart_imports

    smart_imports.all()

    print(utils_a)
    print(utils_b)


Rule 7: modules from parent package
-----------------------------------

If you have sub-packages with the same name in different parts of your project (for example, ``tests`` or ``migrations``), you can allow for them to search modules by name in parent packages.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_local_modules_from_parent",
    #               "suffixes": [".tests"]}]
    # }
    #
    # project on file system:
    #
    # my_package
    # |-- __init__.py
    # |-- a.py
    # |-- tests
    # |-- |-- __init__.py
    # |-- |-- b.py

    # b.py

    import smart_imports

    smart_imports.all()

    print(a)


Rule 8: modules from namespace
------------------------------

The rule allows for modules from a specified package to import by name modules from another package.

.. code-block:: python

    # config:
    # {
    #    "rules": [{"type": "rule_predefined_names"},
    #              {"type": "rule_local_modules_from_namespace",
    #               "map": {"my_package.subpackage_1": ["my_package.subpackage_2"]}}]
    # }
    #
    # project on filesystem:
    #
    # my_package
    # |-- __init__.py
    # |-- subpackage_1
    # |-- |-- __init__.py
    # |-- |-- a.py
    # |-- subpackage_2
    # |-- |-- __init__.py
    # |-- |-- b.py

    # a.py

    import smart_imports

    smart_imports.all()

    print(b)

How to add custom rule?
-----------------------

#. Subclass ``smart_imports.rules.BaseRule``.
#. Implement required logic.
#. Register rule with method ``smart_imports.rules.register``.
#. Add rule to config.
#. ???
#. Profit.

Look into the implementation of current rules, if you need an example.


MyPY
====

Plugin for integration with MyPy implemented.

MyPy config (mypy.ini) example:

.. code-block:: ini

   [mypy]
   plugins = smart_imports.plugins.mypy


Plans
=====

I love the idea of determining code properties by used names. So, I will try to develop it in the borders of ``Smart Imports`` and other projects.

What I planning for ``Smart Imports``:

- Continue support and patch it for new versions of Python.
- Research usage of type annotations to import automatization.
- Try to implement lazy imports.
- Implement utilities for automatic config generation and code refactoring.
- Rewrite part of code in C, to speedup AST construction.
- Implement integrations with popular IDEs.

I open to your suggestions. Feel free to contact me in any way.


.. |pypi| image:: https://img.shields.io/pypi/v/smart_imports.svg?style=flat-square&label=latest%20stable%20version&reset_github_caches=9
    :target: https://pypi.python.org/pypi/smart_imports
    :alt: Latest version released on PyPi

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/smart_imports.svg?style=flat-square&reset_github_caches=9
    :target: https://pypi.python.org/pypi/smart_imports
    :alt: Supported Python versions

.. |test_coverege_develop| image:: https://coveralls.io/repos/github/Tiendil/smart-imports/badge.svg?branch=develop&reset_github_caches=9
    :target: https://coveralls.io/github/Tiendil/smart-imports?branch=develop
    :alt: Test coverage in develop
