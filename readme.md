<a name="readme-top"></a>

<!-- PROJECT NAME -->
<br />
<div align="center">
  <h3 align="center">aep_parser</h3>
  <p align="center">
    An After Effects file parser in Python!
    <br />
    <a href="https://github.com/forticheprod/aep_parser/issues">Report Bug</a>
    ·
    <a href="https://github.com/forticheprod/aep_parser/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


This as a .aep (After Effects Project) parser in Python. After Effects files (.aep) are mostly binary files, encoded in RIFX format. This parser uses [Kaitai Struct](https://kaitai.io/) to parse .aep files and return a Project object containing items, layers, effects and properties.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- INSTALLATION -->
## Installation

```sh
pip install aep-parser
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- USAGE EXAMPLES -->
## Usage

```python
from aep_parser.parsers.project import parse_project

aep_file_path = "01_empty.aep"
project = parse_project(aep_file_path)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/forticheprod/aep_parser/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a merge request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTACT -->
## Contact

Benoit Delaunay - benoit.delaunay@forticheprod.com

Project Link: [https://github.com/forticheprod/aep_parser](https://github.com/forticheprod/aep_parser)

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [aftereffects-aep-parser](https://github.com/boltframe/aftereffects-aep-parser)
* [Kaitai Struct](https://kaitai.io)
* [Lottie](https://lottiefiles.github.io/lottie-docs/aep/)
* [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
