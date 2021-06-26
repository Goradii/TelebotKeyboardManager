import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TelegramBotKeyboardManager",
    packages=["TelegramBotKeyboardManager"],
    version="0.1.0",
    author="Radin Gleb",
    author_email="gleb.rad+pip@gmail.com",
    description="This package help you to organise I/O In pyTelegramBotAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Goradii/TelebotKeyboardManager",
    project_urls={
        "Bug Tracker": "https://github.com/Goradii/TelebotKeyboardManager/issues",
    },
    install_requires=['pyTelegramBotAPI'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
)
