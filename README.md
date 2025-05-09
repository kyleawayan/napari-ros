# napari-ros

[![License BSD-3](https://img.shields.io/pypi/l/napari-ros.svg?color=green)](https://github.com/kyleawayan/napari-ros/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-ros.svg?color=green)](https://pypi.org/project/napari-ros)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-ros.svg?color=green)](https://python.org)
[![tests](https://github.com/kyleawayan/napari-ros/workflows/tests/badge.svg)](https://github.com/kyleawayan/napari-ros/actions)
[![codecov](https://codecov.io/gh/kyleawayan/napari-ros/branch/main/graph/badge.svg)](https://codecov.io/gh/kyleawayan/napari-ros)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-ros)](https://napari-hub.org/plugins/napari-ros)

Code for ["Assessment and Validation of a Computer Vision Algorithm for Wildfire Rate of Spread Estimation"](https://www.mdpi.com/2571-6255/7/12/457). Documentation is WIP.

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Usage

Please see the [manual README](./manual.md).

## Installation

~~You can install `napari-ros` via [pip]:~~ Package is not published yet.

To install latest development version :

    pip install git+https://github.com/kyleawayan/napari-ros.git

## Creating New Version

```sh
# the tag will be used as the version string for your package
# make it meaningful: https://semver.org/
git tag -a v0.1.0 -m "v0.1.0"

# make sure to use follow-tags so that the tag also gets pushed to github
git push --follow-tags
```

Then, build the package:

```py
python -m build .
```

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-ros" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/kyleawayan/napari-ros/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

## Citation

If you use this napari plugin or code for your research, we would appreciate a citation:
```
@Article{fire7120457,
  AUTHOR = {Ameri, Ehsan and Awayan, Kyle and Cobian-Iñiguez, Jeanette},
  TITLE = {Assessment and Validation of a Computer Vision Algorithm for Wildfire Rate of Spread Estimation},
  JOURNAL = {Fire},
  VOLUME = {7},
  YEAR = {2024},
  NUMBER = {12},
  ARTICLE-NUMBER = {457},
  URL = {https://www.mdpi.com/2571-6255/7/12/457},
  ISSN = {2571-6255},
  ABSTRACT = {As wildfire activity increases worldwide, developing effective methods for estimating how fast it can spread is critical. This study aimed to develop and validate a computer vision algorithm for fire spread estimation. Using visual flame data from laboratory experiments on excelsior and pine needle fuel beds, we explored fire spread predictions for two types of experiments. In the first, the experiments were conducted in an environment where the flame was maintained visually undisturbed while in the second, real-world scenarios were simulated with visual obstructions. Algorithm performance evaluation was conducted by computing the index of agreement and normalized root mean square deviation (NRMSD) error. Results show that the algorithm estimates fire spread well in pristine visual environments with varying accuracy depending on the fuel type. For instance, the index of agreement between the rate of spread values estimated by the algorithm and the measured values is 0.56 for excelsior fuel beds and 0.51 for pine needle fuel beds. For visual obstructions, varying impacts on the rate of spread predictions were observed. Adding an orange background behind the flame had the least effect on algorithm performance (IAmedian = 0.45), followed by placing a Y-shape element resembling a branch (IAmedian = 0.31) and adding an LED light near the flame (IAmedian = 0.30).},
  DOI = {10.3390/fire7120457}
}
```
