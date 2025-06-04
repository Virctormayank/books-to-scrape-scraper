from setuptools import setup, find_packages

setup(
    name='books_scraper',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'books-scraper = books_scraper.cli:main',
        ],
    },
    author='Mayank',
    description='CLI tool to scrape books.toscrape.com based on price/category',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
