# Pheniqs build tool

`pheniqs-build-api.py` is a tool for building various binary versions of Pheniqs, it is essentially a compact package manager just for Pheniqs. It builds an entire virtual root of all the dependencies and compiles a binary executable of Pheniqs against that root. `pheniqs-build-api.py` takes a small JSON configuration file that tells it where to download source code for all the libraries Pheniqs depends on. You can find various build configurations in the build folder.

Of particular interest is the configuration for building a [statically linked](https://en.wikipedia.org/wiki/Static_library) binary since it does not require elevated permissions and can be used on cluster environments. It produces a binary that entirely self contained and does not link against external dynamic libraries. This means it does not depend on which version, for instance, of HTSLib is preinstalled on the cluster. A comfortable side effect of static linking is that the binary can be moved anywhere in the path, or to any other machine with a similar Operating System and CPU, without effecting its functionality.  

Before you use `pheniqs-build-api.py` you will need to have a C/C++ compiler available on your system. For Ubuntu Linux that usually invoves installing the `build-essential` package:

```shell
apt-get install -y build-essential
```

while on MacOS you will need to install [Xcode](https://apps.apple.com/us/app/xcode/id497799835) from the App Store

## Building a Pheniqs binary with `pheniqs-build-api.py`

For example to build a static binary of the latest trunk Pheniqs code from github you can use the `trunk_static.json` configuration:

```shell
% ./pheniqs-build-api.py build build/trunk_static.json
INFO:Package:unpacking zlib 1.2.11
INFO:Package:configuring make environment zlib 1.2.11
INFO:Package:building with make zlib 1.2.11
INFO:Package:installing with make zlib 1.2.11
INFO:Package:unpacking bz2 1.0.6
INFO:Package:building with make bz2 1.0.6
INFO:Package:installing with make bz2 1.0.6
INFO:Package:unpacking xz 5.2.4
INFO:Package:configuring make environment xz 5.2.4
INFO:Package:building with make xz 5.2.4
INFO:Package:installing with make xz 5.2.4
INFO:Package:unpacking libdeflate 1.0
INFO:Package:building with make libdeflate 1.0
INFO:Package:unpacking htslib 1.9
INFO:Package:configuring make environment htslib 1.9
INFO:Package:building with make htslib 1.9
INFO:Package:installing with make htslib 1.9
INFO:Package:unpacking rapidjson 1.1.0
INFO:Package:downloaded archive saved pheniqs 2.0-trunk None
INFO:Package:unpacking pheniqs 2.0-trunk
INFO:Package:building with make pheniqs 2.0-trunk
INFO:Package:installing with make pheniqs 2.0-trunk
```

When execution is finished you may inspect your virtual root in the `bin/trunk_static/install`. Statically linked builds made with `pheniqs-build-api.py` will also report the versions of all built in libraries.

```Shell
% ./bin/trunk_static/install/bin/pheniqs --version
pheniqs version 2.0.4
zlib 1.2.11
bzlib 1.0.6
xzlib 5.2.4
libdeflate 1.0
rapidjson 1.1.0
htslib 1.9
```

You can check that your binary indeed does not link against any of the dependencies dynamically with `ldd` on Linux:

```shell
% ldd pheniqs
	linux-vdso.so.1 =>  (0x00007ffff3300000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007f6910e2d000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f6910b24000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f691090e000)
	libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f69106f1000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f6910327000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f69111af000)
```

or `otool` on MacOs:

```shell
% otool -L ./bin/trunk_static/install/bin/pheniqs
./bin/trunk_static/install/bin/pheniqs:
	/usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 400.9.4)
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1252.200.5)
```

## *Building with the Makefile*
If you wish, you can of course build Pheniqs directly with the provided Makefile against dynamic libraries installed on your system as described in the Pheniqs install page.
