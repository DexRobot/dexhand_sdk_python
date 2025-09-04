from setuptools import setup, find_packages

setup(
    name="dexhand_sdk_python",
    version="1.0.0",
    description="Fundamental controlling library of DexHand-021 product series of DexRobot, Inc.",
    author="DexRobot",
    author_email="contact@dexrobot.com",
    url="https://www.dex-robot.com",
    packages=find_packages(),

    data_files=[
    ],

    package_data={
        'dexhand_sdk_python': ['cpp/sdk/lib/linux/libdexhand.so',
                               'cpp/sdk/lib/linux/libusbcanfd.so',
                               'cpp/sdk/lib/linux/libusbcanfd.so.1.0.8',
                               'cpp/sdk/lib/linux/libusb-1.0.so',
                               'cpp/sdk/lib/linux/libControlCAN.so'],
    },
    include_package_data=True,

    exclude_package_data={
    },

    install_requires=[],

    extras_require={
        'docs': [
            'sphinx>=8.1.3',
            'sphinx-rtd-theme>=1.3.0',
            'sphinx-autodoc-typehints',
        ],
    },

    python_requires='>=3.10',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Robotics',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
    ],
)
