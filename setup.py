
import setuptools


with open("README.rst", "r") as f:
    long_description = f.read()


setuptools.setup(
    name='smart_imports',
    version='0.2.4',
    description='automatic importing for Python modules',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url='https://github.com/Tiendil/smart-imports',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['python', 'import'],
    packages=setuptools.find_packages(),
    install_requires=[],

    include_package_data=True)
