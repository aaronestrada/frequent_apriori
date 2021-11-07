from distutils.core import setup

setup(
    name='frequent_apriori',
    version='1.0',
    description='Find frequent patterns on set of transactions using the Apriori algorithm',
    license='BSD',
    author='Aaron Estrada Poggio',
    author_email='aaron.estrada.poggio@gmail.com',
    url='https://github.com/aaronestrada/frequent_apriori',
    include_package_data=True,
    packages=['frequent_apriori'],
    python_requires='>=3.6',
    install_requires=[

    ]
)
